from .generate import GeneratorFactory

def main() -> None:
    generator = GeneratorFactory.get_instance()
    print(generator.generate("Hello !"))

if __name__ == "__main__":
    main()
