#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload"

# 同时尝试的 series：s = May/June, w = Oct/Nov
SERIES_LIST = ["s", "w"]

# 试卷类型：题卷(qp) + 评分标准(ms)
COMPONENT_TYPES = ["qp", "ms"]

# 试卷编号分组
PAPER_GROUPS = []
for i in range(1, 5):
    PAPER_GROUPS.append([f"{i}{j}" for j in range(1, 5)])


def show_help():
    """自定义帮助信息"""
    help_text = """
📘 用法示例:
    python fetch_pastpapers.py -s 9618 -b 20 -e 25

📗 参数说明:
    -s, --subject        学科代码（4位整数，如 9618）
    -b, --begin          开始年份（两位数，15–25，默认 15）
    -e, --end            结束年份（两位数，15–25，默认 25，必须 ≥ begin）
    -o, --output-dir     保存目录（默认: /media）
    -t, --threads        并发下载线程数（默认: 8）

📙 下载范围 (固定逻辑):
    • SERIES:  s, w  （例如：s20, w20, s21, w21, ...）
    • PAPER:   qp 和 ms
    • 试卷编号: 11–14, 21–24, 41–44
      例如：qp_11, qp_12, ..., ms_41, ms_42, ...

📒 文件名模式:
    {subject}_{series}{yy}_{type}_{code}.pdf

    例如 (subject=9618, year=2024):
        9618_s24_qp_11.pdf
        9618_s24_ms_23.pdf
        9618_w24_qp_44.pdf
"""
    print(help_text)
    sys.exit(0)


def parse_args():
    # 若用户没参数或输入问号／help，则显示帮助
    if len(sys.argv) == 1 or sys.argv[1] in ["?", "-?", "--help"]:
        show_help()

    parser = argparse.ArgumentParser(
        description="批量下载 Papacambridge CAIE past papers PDF",
        add_help=False,
    )

    parser.add_argument(
        "-s",
        "--subject",
        required=True,
        type=int,
        help="学科代码（4位整数，例如 9618）",
    )

    parser.add_argument(
        "-b",
        "--begin",
        "--start-year",
        "--start_year",
        dest="start_year",
        type=int,
        default=15,
        help="开始年份（2位数，15–25，默认 15）",
    )

    parser.add_argument(
        "-e",
        "--end",
        "--end-year",
        "--end_year",
        dest="end_year",
        type=int,
        default=25,
        help="结束年份（2位数，15–25，默认 25，必须 ≥ begin）",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default="/media",
        help="下载保存的目录（默认：/media）",
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=8,
        help="并发下载线程数（默认：8）",
    )

    parser.add_argument(
        "--help",
        action="store_true",
        help="显示帮助信息并退出",
    )

    args = parser.parse_args()

    if args.help:
        show_help()

    return args


def validate_args(args):
    if not (1000 <= args.subject <= 9999):
        sys.exit("❌ subject 必须是 4 位整数，例如 9618")

    if not (15 <= args.start_year <= 25):
        sys.exit("❌ begin/start_year 必须在 15 到 25 之间，例如 15 表示 2015")

    if not (15 <= args.end_year <= 25):
        sys.exit("❌ end/end_year 必须在 15 到 25 之间，例如 25 表示 2025")

    if args.end_year < args.start_year:
        sys.exit("❌ end_year 必须大于或等于 start_year")

    if args.threads <= 0:
        sys.exit("❌ threads 必须是正整数，例如 4 或 8")


def download_file(url: str, dest: Path) -> bool:
    """
    下载单个文件。
    成功返回 True，失败返回 False（404 / HTML 跳转 / 其他错误）。
    """
    try:
        resp = requests.get(url, stream=True, timeout=20)
    except requests.RequestException as e:
        print(f"  ⚠️ 请求失败：{e}")
        return False

    # ① 判断 HTTP 状态码
    if resp.status_code == 404:
        print("  ❌ 404 Not Found，跳过。")
        return False
    elif resp.status_code != 200:
        print(f"  ❌ HTTP {resp.status_code}，跳过。")
        return False

    # ② 检查 Content-Type
    content_type = resp.headers.get("Content-Type", "").lower()
    if "pdf" not in content_type:
        # 有些返回 HTML 时 Content-Type 是 text/html
        print(f"  ⚠️ 非 PDF 文件 (Content-Type={content_type})，跳过。")
        return False

    # ③ 检查文件头是否为 %PDF-
    try:
        first_chunk = next(resp.iter_content(chunk_size=5))
        if not first_chunk.startswith(b"%PDF-"):
            print("  ⚠️ 文件头不是 PDF 格式，跳过。")
            return False
    except StopIteration:
        print("  ⚠️ 响应为空文件，跳过。")
        return False

    # ④ 真正写入文件（包括第一块）
    try:
        with dest.open("wb") as f:
            f.write(first_chunk)
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except OSError as e:
        print(f"  ⚠️ 写入文件失败 {dest}：{e}")
        return False

    print(f"  ✅ 下载完成：{dest}")
    return True



def main():
    args = parse_args()
    validate_args(args)

    subject_str = f"{args.subject:04d}"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"📚 科目代码：{subject_str}")
    print(f"📅 年份范围：{args.start_year:02d} ~ {args.end_year:02d}")
    print(f"📂 输出目录：{out_dir.resolve()}")
    print(f"📌 SERIES：{', '.join(SERIES_LIST)}")
    print(f"📌 类型：{', '.join(COMPONENT_TYPES)}")
    print(f"📌 线程数：{args.threads}")
    print()

    # 按年份循环
    for year in range(args.start_year, args.end_year + 1):
        yy = f"{year:02d}"
        print(f"\n==================== 年份：20{yy} ====================")

        # 按 series s/w
        for series in SERIES_LIST:
            print(f"\n➡ SERIES: {series}{yy}")
            year_abort = False  # 标记是否中断本年份（某个分组全部失败）

            # 按 group (11~14, 21~24, 41~44)
            for group in PAPER_GROUPS:
                group_str = f"{group[0]}–{group[-1]}"
                print(f"  ▶ 尝试试卷编号组：{group_str}")
                group_success = False

                # 为当前 group 构建任务列表，并发下载
                futures = []
                with ThreadPoolExecutor(max_workers=args.threads) as executor:
                    for paper_code in group:
                        paper_suffix = paper_code

                        for comp_type in COMPONENT_TYPES:
                            filename = f"{subject_str}_{series}{yy}_{comp_type}_{paper_suffix}.pdf"
                            url = f"{BASE_URL}/{filename}"
                            print(url)
                            dest = out_dir / filename

                            if dest.exists():
                                print(f"    ⏭ 已存在，跳过：{filename}")
                                group_success = True
                                continue

                            print(f"    ⬇️ 正在下载：{filename}")
                            print(f"       URL: {url}")
                            future = executor.submit(download_file, url, dest)
                            futures.append(future)

                    # 收集当前 group 所有任务的结果
                    for future in as_completed(futures):
                        try:
                            ok = future.result()
                        except Exception as e:
                            print(f"  ⚠️ 下载线程异常：{e}")
                            ok = False
                        if ok:
                            group_success = True

                # 一个分组结束，若完全没有成功的文件，则终止本年份
                if not group_success:
                    print(f"  ⚠️ 整个试卷编号组 {group_str} 在 {series}{yy} 中全部下载失败。")
                    print("  ⛔ 结束该年份的下载，进入下一年份。")
                    year_abort = True
                    break  # 结束当前年份的 group 循环

            if year_abort:
                break  # 结束当前年份的 series 循环，继续下一个年份


if __name__ == "__main__":
    main()
