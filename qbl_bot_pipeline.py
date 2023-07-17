import subprocess
import sys
import qbl_bot
import yaml


def create_pages(skillmap_path, dst_dir):
    """Main loop for creating pages from a skillmap"""
    skillmap = read_skillmap(skillmap_path)
    for _, unit in skillmap.items():
        unit_name = unit['unit_name']
        questions_per_skill = int(unit['questions_per_skill'])
        page_count = 1
        while True:
            page_key = f"page-{page_count}"
            if page_key not in unit:
                break
            page = unit[page_key]
            page_name = page['page_name']
            skills = page['skills']
            created_page_path = qbl_bot.main(skills, unit_name, page_name, questions_per_skill, dst_dir)
            subprocess.run(["bash", "create_PR.sh", created_page_path], check=True)
            page_count += 1


def read_skillmap(skillmap_path):
    with open(skillmap_path) as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python qbl_bot_pipeline.py <skillmap_path> <dst_dir>")
        exit(1)
    skillmap_path = sys.argv[1]
    dst_dir = sys.argv[2]
    create_pages(skillmap_path, dst_dir)