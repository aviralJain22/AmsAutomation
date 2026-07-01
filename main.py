import sys
from helpers.logger import get_logger
from workflow.ams360_workflow import AMS360Workflow

logger = get_logger("main")


def main() -> None:
    try:
        AMS360Workflow(headless=False).run()
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
