def test_includes_project_path(init_tester, project_path):
    init_tester.execute(f'"{project_path}"')

    assert f"{project_path}" in init_tester.io.fetch_output()


def test_dry_run(init_tester, project_path):
    init_tester.execute(f'--dry-run "{project_path}"')

    assert "dry run" in init_tester.io.fetch_output()
