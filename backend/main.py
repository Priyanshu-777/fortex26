import sys
from dotenv import load_dotenv
from core.orchestrator import Orchestrator

def main():
    load_dotenv()
    print("Starting AI Bug Bounty Agent...")
    
    # Initialize implementation here
    orchestrator = Orchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
