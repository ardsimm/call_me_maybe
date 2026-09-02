from src.constrainer.constrainer import Constrainer
from src.constrainer.constrainer_factory import ConstrainerFactory
from src.prompting.prompting import Prompting
from src.state import StateFactory, StateType, State
from src.models.function import Parameter, ParameterType, Function
from typing import List, Optional

from src.state.__trie_state import TrieState
from .generator import Generator


class GeneratorImpl(Generator):
    """Default `Generator`: constrained token-by-token decoding.

    Every generated value is decoded as a quoted JSON string regardless
    of its target type (int/float/bool/string all end on a
    `string_end_sequences` token), then trimmed to the first unescaped
    `"` before being parsed back into the target Python type by the
    caller.
    """

    TOKEN_GEN_LIMIT = 67

    def __find_unescapted_quote_idx(self, s: str) -> int:
        """Return the index of the first unescaped `"` in `s`, or -1.

        A `"` is escaped if it is preceded by an odd number of
        consecutive backslashes; `escape_count` resets to 0 on any
        non-backslash character so an earlier, unrelated backslash run
        cannot make a later quote look escaped.

        Parameters
        ----------
        s : str
            The text to search.

        Returns
        -------
        int
            The index of the first unescaped `"`, or -1 if none is found.
        """
        idx = 0
        escape_count = 0
        for char in s:
            if char == "\\":
                escape_count += 1
                idx += 1
                continue
            if char == '"' and not escape_count % 2:
                return idx
            escape_count = 0
            idx += 1
        return -1

    def __strip_completion(self, completion: str) -> str:
        """Trim `completion` to everything before its first unescaped `"`.

        Parameters
        ----------
        completion : str
            The raw decoded completion text.

        Returns
        -------
        str
            `completion` up to (excluding) its first unescaped `"`. If
            none is found, returns `""` (slicing with a -1 stop index).
        """
        return completion[: self.__find_unescapted_quote_idx(completion)]

    def __handle_escaped_quotes(self, completion: str) -> str:
        """Unescape `\\"` sequences into plain `"` in `completion`.

        Parameters
        ----------
        completion : str
            The stripped completion text, possibly containing escaped
            quotes.

        Returns
        -------
        str
            `completion` with every `\\"` replaced by `"`.
        """
        return completion.replace('\\"', '"')

    def __get_next_token(
        self, result: List[int], constrainer: Constrainer
    ) -> Optional[int]:
        """Pick the next token id for the sequence `result`.

        Parameters
        ----------
        result : list of int
            The token ids generated so far (prompt + completion).
        constrainer : Constrainer
            The constrainer picking the next token from the model's
            logits for `result`.

        Returns
        -------
        int or None
            The picked token id, or None if the constrainer's state
            signals generation is complete.

        Raises
        ------
        ValueError
            Forwarded from `Constrainer.pick_token` if its state is
            unconstrained and the logits are empty.
        GenerationError
            Forwarded from `Constrainer.pick_token` if the picked token
            is rejected by its state.
        """
        allowed_tokens = constrainer.state.get_allowed_tokens()
        if allowed_tokens is None:
            return None
        token = constrainer.pick_token(
            self.model.get_logits_from_input_ids(result)
        )
        return token

    def __get_completion(self, prompt: str, constrainer: Constrainer) -> str:
        """Decode `prompt` token by token until `constrainer` signals stop.

        Generation also stops once `TOKEN_GEN_LIMIT` tokens have been
        produced, as a safety cap against a state that never signals
        completion.

        Parameters
        ----------
        prompt : str
            The prompt to complete.
        constrainer : Constrainer
            The constrainer driving token selection for this completion.

        Returns
        -------
        str
            The decoded completion text (excluding the prompt).

        Raises
        ------
        ValueError
            Forwarded from `__get_next_token`.
        GenerationError
            Forwarded from `__get_next_token`.
        """
        result: List[int] = self.tokenizer.encode(prompt).tolist()[0]
        initial_len = len(result)
        token = self.__get_next_token(result, constrainer)
        token_count = 0
        while token is not None and token_count < self.TOKEN_GEN_LIMIT:
            result.append(token)
            if isinstance(constrainer.state, TrieState):
                determinated_branch = (
                    constrainer.state.trie.get_determinated_branch(
                        constrainer.state.current_node
                    )
                )
                if determinated_branch is not None:
                    result.extend(determinated_branch)
                    break
            token = self.__get_next_token(result, constrainer)
            token_count += 1
        return self.tokenizer.decode(result[initial_len:])

    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        """Generate the name of the function `prompt` should call.

        Decodes against a `TrieState` built from every candidate
        function's encoded name, so only a valid name can be produced.

        Parameters
        ----------
        prompt : str
            The user's natural-language request.
        functions : list of Function
            Every candidate function the model may choose among.

        Returns
        -------
        str
            The chosen function's name.

        Raises
        ------
        GenerationError
            Forwarded from building the `TrieState` or from decoding
            (see `__get_completion`).
        ValueError
            Forwarded from decoding (see `__get_completion`).
        """
        print("Generating name...")

        prompt = Prompting.build_name_generation_prompt(prompt, functions)
        result = self.__get_completion(
            prompt=prompt,
            constrainer=ConstrainerFactory.get_instance(
                StateFactory.get_trie_state_instance(
                    [
                        self.tokenizer.encode(function.name).tolist()[0]
                        for function in functions
                    ]
                )
            ),
        )
        return self.__strip_completion(result)

    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        """Generate a value for each of `function`'s parameters.

        Parameters are generated in declaration order, one at a time,
        each one's prompt threading every previously generated
        parameter's value as context. The `State` used for each
        parameter is picked from its `ParameterType`: `IntState`,
        `FloatState`, a `TrieState` over `"true"`/`"false"` for `BOOL`,
        or `StringState` otherwise.

        Parameters
        ----------
        prompt : str
            The user's natural-language request.
        function : Function
            The function whose parameters should be filled in.

        Returns
        -------
        list of Parameter
            One `Parameter` per `function.parameters`, in order, with
            `value` set from generation and any escaped quotes in it
            unescaped.

        Raises
        ------
        GenerationError
            Forwarded from building a `TrieState` (for `BOOL` parameters)
            or from decoding (see `__get_completion`).
        ValueError
            Forwarded from decoding (see `__get_completion`).
        """
        print("Generating parameters...")

        parameters: List[Parameter] = []
        user_prompt = prompt
        last_parameter: Optional[Parameter] = None
        prompt = Prompting.build_parameter_generation_prompt(
            user_prompt, function
        )
        for parameter in function.parameters:
            parameter.value = None
            prompt = Prompting.build_next_parameter_generation_prompt(
                prompt, function, parameter, last_parameter
            )
            state: State = StateFactory.get_instance(StateType.STRING_STATE)
            if parameter.type == ParameterType.INT:
                state = StateFactory.get_instance(StateType.INT_STATE)
            elif parameter.type == ParameterType.FLOAT:
                state = StateFactory.get_instance(StateType.FLOAT_STATE)
            elif parameter.type == ParameterType.BOOL:
                state = StateFactory.get_trie_state_instance(
                    [
                        self.tokenizer.encode(value).tolist()[0]
                        for value in ["true", "false"]
                    ]
                )

            result = self.__get_completion(
                prompt=prompt,
                constrainer=ConstrainerFactory.get_instance(state),
            )
            stripped_result = self.__strip_completion(result)
            parameter.value = stripped_result
            last_parameter = Parameter(
                name=parameter.name, type=parameter.type, value=parameter.value
            )
            parameters.append(
                Parameter(
                    name=parameter.name,
                    type=parameter.type,
                    value=self.__handle_escaped_quotes(parameter.value),
                )
            )

        return parameters
