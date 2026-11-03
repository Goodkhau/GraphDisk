import nox

@nox.session
def e2e(session):
    session.install(".")
    session.install("pytest")
    session.run("pytest", "-m", "e2e", "-o", "addopts=")