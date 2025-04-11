import asyncio
from kernel_client import KernelClient

async def main():
    async with KernelClient("http://localhost:8888") as client:
        code = '''
        import requests
        from bs4 import BeautifulSoup
        import lxml
        from tabulate import tabulate
        from openpyxl import Workbook

        # 获取网页内容（示例：一个包含 HTML 表格的页面）
        url = "https://www.w3schools.com/html/html_tables.asp"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")

        # 找到表格
        table = soup.find("table")

        # 解析表头
        headers = [th.text.strip() for th in table.find_all("th")]

        # 解析表格内容
        rows = []
        for tr in table.find_all("tr")[1:]:
            cols = tr.find_all("td")
            if cols:
                rows.append([td.text.strip() for td in cols])

        # 打印格式化表格
        print("格式化表格：")
        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # 保存到 Excel 文件
        wb = Workbook()
        ws = wb.active
        ws.title = "HTML Table Data"

        # 写入表头
        ws.append(headers)

        # 写入内容
        for row in rows:
            ws.append(row)

        wb.save("table_data.xlsx")
        print("数据已保存为 table_data.xlsx")
        '''

        # 安装所需包
        required_packages = ['requests', 'beautifulsoup4', 'lxml', 'tabulate', 'openpyxl']
        install_result = await asyncio.wait_for(client.install_packages(required_packages), timeout=20)
        if install_result.success:
            print("\n安装成功:", install_result.output)
        else:
            print("安装失败:", install_result.error)

        # 执行代码
        result = await asyncio.wait_for(client.execute_code(code), timeout=20)
        print("\n执行结果:")
        if result.success:
            print(result.output)
        else:
            print("错误:", result.error)

if __name__ == "__main__":
    asyncio.run(main())
