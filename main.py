# main.py

from services.operations_service import OperationsService

def main():
    svc = OperationsService()
    svc.run()

if __name__ == "__main__":
    main()
