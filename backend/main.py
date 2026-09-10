from fastapi import FastAPI

from controller.auth_route import router as auth_router

app = FastAPI()
app.include_router(auth_router)


def main():
    print("Hello from backend!")


if __name__ == "__main__":
    main()
