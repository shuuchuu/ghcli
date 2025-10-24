import gradio as gr

from .api import create_issue, list_issues
from .model import Issue


def _format_issue(issue: Issue) -> str:
    return f"""[{issue.title}]({issue.url})\n\n{issue.body}"""


def _list_issues_wrapper(owner: str, repo: str) -> str:
    issues = list_issues(owner, repo)
    return "\n\n---\n\n".join(map(_format_issue, issues)) if issues else "No issue"


def _create_issue_wrapper(owner: str, repo: str, title: str, body: str) -> str:
    return _format_issue(create_issue(owner, repo, title, body))


def gradio() -> None:
    with gr.Blocks(title="GHCLI — Gradio UI", theme=None) as demo:
        gr.Markdown(
            "# GHCLI — Gradio UI\nA small GUI on top of the `ghcli` idea: list issues and create issues using GitHub API.\n"
        )

        with gr.Tabs():
            with gr.TabItem("List issues"):
                with gr.Row():
                    owner_in = gr.Textbox(
                        label="Owner", placeholder="e.g. octocat", value=""
                    )
                    repo_in = gr.Textbox(
                        label="Repo", placeholder="e.g. hello-world", value=""
                    )
                md_out = gr.Markdown(label="Issues", value="")
                list_btn = gr.Button("List issues")

                list_btn.click(
                    fn=_list_issues_wrapper,
                    inputs=[owner_in, repo_in],
                    outputs=md_out,
                )

            with gr.TabItem("Create issue"):
                with gr.Row():
                    owner2 = gr.Textbox(label="Owner", placeholder="e.g. octocat")
                    repo2 = gr.Textbox(label="Repo", placeholder="e.g. hello-world")
                title_in = gr.Textbox(label="Issue title")
                body_in = gr.Textbox(label="Issue body", lines=6)
                create_btn = gr.Button("Create issue")
                create_md = gr.Markdown(label="Issue")

                create_btn.click(
                    fn=_create_issue_wrapper,
                    inputs=[owner2, repo2, title_in, body_in],
                    outputs=[create_md],
                )

    demo.launch()
