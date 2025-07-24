from aged_care_pipeline.services.operations_service import OperationsService
from aged_care_pipeline.utils.logger import setup_logger


def main():
    setup_logger()
    service = OperationsService()
    service.run()


if __name__ == "__main__":
    main()
