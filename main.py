def main() -> None:
    from aged_care_pipeline.services.operations_service import OperationsService

    OperationsService().run()


if __name__ == "__main__":
    main()
