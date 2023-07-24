import subprocess
import sys
import qbl_bot
import yaml


def create_pages(skillmap_path, dst_dir):
    """Main loop for creating pages from a skillmap"""
    skillmap = read_skillmap(skillmap_path)
    for key, unit_dict in skillmap.items():
        if not key.startswith("unit_"):
            continue     
        unit_name = unit_dict['unit_name']
        page_count = 1
        while True:
            page_key = f"page-{page_count}"
            if page_key not in unit_dict:
                break
            page_dict = unit_dict[page_key]
            page_name = page_dict['page_name']
            skills = page_dict['skills']
            created_page_path = qbl_bot.generate_page(unit_name, page_name, skills, int(skillmap["questions_per_skill"]), dst_dir, skillmap["role_description"], skillmap["course_description"])
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
