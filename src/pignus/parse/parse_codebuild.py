"""Parse CodeBuild

"""


def import_failure(build_logs: list):
    """Parse the import failure and attempt to assign a reason for the import failure."""
    access_denied_error = "Error response from daemon: pull access denied"
    for log_line in build_logs:
        if access_denied_error in log_line["message"]:
            return "ecr-auth"
    return False


def successful_sync(build_logs: list) -> str:
    digest = None
    count = 0
    select_digest = False
    for log_line in build_logs:
        if "Running command docker push" in log_line["message"]:
            select_digest = True
        if select_digest and "digest: sha256:" in log_line["message"]:
            msg = log_line["message"]
            digest = msg[msg.find("digest: sha256:") + 15: msg.find("size:") - 1]
        count += 1

    return digest

# End File: automox/src/pignus/parse/parse_codebuild.py
