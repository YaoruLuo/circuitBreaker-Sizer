import json
from datetime import datetime
import os

def write_llm_log(
    user_input, breaker_structured, trip_structured, table_rows,
    log_path, max_entries
):
    def strip_trip_desc(rows):
        clean = []
        for row in rows or []:
            row = dict(row)
            row.pop("脱扣器描述", None)
            clean.append(row)
        return clean

    # 推荐结果表格式美化
    def format_table(rows):
        if not rows:
            return "无匹配推荐"
        lines = []
        headers = None
        for idx, row in enumerate(rows):
            filtered = {k: row[k] for k in ["产品序列号", "订货号"] if k in row}
            if idx == 0:
                headers = list(filtered.keys())
                lines.append("  |  ".join(headers))
                lines.append("-" * (len(lines[0]) + 2))
            values = [str(filtered.get(h, "")) for h in headers]
            lines.append("  |  ".join(values))
        return "\n".join(lines)

    # 日志分割符
    divider = "\n\n" + "="*60 + "\n\n"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # log entry 内容（记录时间在内部）
    log_entry = [
        f"记录时间: {now}",
        f"【用户输入】\n{user_input}\n",
        "【断路器结构化输出】",
        json.dumps(breaker_structured, ensure_ascii=False, indent=2),
        "【脱扣器结构化输出】",
        json.dumps(trip_structured, ensure_ascii=False, indent=2),
        "【推荐结果表】",
        format_table(strip_trip_desc(table_rows))
    ]
    new_record = "\n\n".join(log_entry)

    # 日志目录不存在则创建
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 读取旧日志
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # 用divider分割
    records = [r for r in content.split(divider) if r.strip()]
    records.append(new_record)
    if len(records) > max_entries:
        records = records[-max_entries:]
    final_log = divider.join(records)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(final_log)
