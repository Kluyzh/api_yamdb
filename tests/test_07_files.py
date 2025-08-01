import os

from tests.conftest import MANAGE_PATH, project_dir_content, root_dir_content

api_path = os.path.join(MANAGE_PATH, 'api')
if 'api' in project_dir_content and os.path.isdir(api_path):
    api_dir_content = os.listdir(api_path)
    assert 'permissions.py' not in api_dir_content, (
        f'В директории `{api_path}` не должно быть файла с моделями. '
        'В этом приложении они не нужны.'
    )
else:
    assert False, f'Не найдено приложение `api` в папке {MANAGE_PATH}'


# test .md
default_md = '# api_yamdb\napi_yamdb\n'
filename = 'README.md'
assert filename in root_dir_content, (
    f'В корне проекта не найден файл `{filename}`'
)

with open(filename, 'r', errors='ignore') as f:
    file = f.read()
    assert file != default_md, (
        f'Не забудьте оформить `{filename}`'
    )
