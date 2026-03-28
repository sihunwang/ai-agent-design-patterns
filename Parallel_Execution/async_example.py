import asyncio  # Python의 비동기 처리를 위한 asyncio 라이브러리 불러오기


# 비동기 함수 정의 (coroutine)
async def say_hello(n):
    await asyncio.sleep(1)  # 1초 동안 비동기 대기 (다른 작업이 실행될 수 있음)
    print(f"{n}번 인사")  # 인사 메시지 출력


# 메인 비동기 함수 정의
async def main():

    # 여러 비동기 작업을 동시에 실행하고
    # await : gather 내 모든 작업이 끝날 때까지 기다림
    # asyncio.gather()는 여러 비동기 작업을 동시에 실행하고 모두 끝날 때까지 기다리는 함수 -> 결과 한 번에 반환 (호출한 순서대로)
    await asyncio.gather(   # gather: 비동기 작업 동시 실행
        say_hello(1),  # 첫 번째 비동기 작업
        say_hello(2),  # 두 번째 비동기 작업
    )
    # asyncio.as_completed(task): 여러 비동기 작업을 동시에 실행, 작업이 끝나는 대로 결과 반환   

    # 위 두 작업이 모두 끝난 후 실행
    print("완료!")


# 프로그램 시작점
# 이벤트 루프를 생성하고 main() 비동기 함수를 실행
asyncio.run(main())