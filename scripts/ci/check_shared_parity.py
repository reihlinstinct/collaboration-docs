"""Shadow comparison only. Findings never leave memory or appear in output."""
import importlib.util
import os
from pathlib import Path
import sys


def normalized(findings):
    return sorted((f.path, f.rule, f.scope, f.evidence) for f in findings)


def main():
    try:
        root = Path(os.environ['CALLER_ROOT']).resolve(strict=True)
        trusted = Path(os.environ['TRUSTED_ROOT']).resolve(strict=True)
        if root == trusted or root in trusted.parents or trusted in root.parents:
            raise ValueError()
        spec = importlib.util.spec_from_file_location('old_guard', root/'scripts/security/scorecard_guard.py')
        old = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = old
        spec.loader.exec_module(old)
        sys.path.insert(0, str(trusted/'src'))
        from repo_checks.inputs import Inputs
        from repo_checks.wrapper import scan
        before = normalized(old.scan(root))
        with Inputs(root) as inputs:
            after = normalized(scan(inputs))
        if before != after:
            raise ValueError()
        print('Shared/old normalized parity: pass')
        return 0
    except Exception:
        print('Shared/old normalized parity: failed')
        return 1


if __name__ == '__main__':
    sys.exit(main())
