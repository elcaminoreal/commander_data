# Testing Philosophy for commander_data

## Core Principle: Test Public Interfaces Only

This codebase follows a strict testing philosophy: **internal/private functions are never tested directly**.

### Why We Don't Test Internal Functions

1. **Avoid Brittleness**: Testing internal implementation details creates brittle tests that break whenever refactoring occurs, even when the public behavior remains unchanged.

2. **Enable Refactoring**: By only testing the public API, we maintain the freedom to refactor internal implementation without having to update tests. This encourages continuous improvement of the codebase.

3. **Focus on Contracts**: Tests should verify that the public contract (the API users interact with) works correctly. If the public interface works as expected, the internal details are working correctly too.

4. **Maintainability**: When implementation changes are needed, we only need to update the code, not both the code and a suite of internal tests.

### What We Test

- **Public functions and classes** exported in `__init__.py`
- **Public methods** on classes that users will call
- **Public constants and exports** like `COMMAND`, `GIT`, `DOCKER`, etc.
- **Behavior and contracts** rather than implementation

### What We Don't Test

- Functions prefixed with underscore (e.g., `_get_value_parts`, `_parse_kwargs`, `_really_run`)
- Internal helper methods
- Private implementation details that support public APIs
- Internal data structures not exposed to users

### How to Write Good Tests

Instead of testing internal functions directly, test them **indirectly through the public API**:

```python
# DON'T: Test internal function directly
def test_parse_kwargs():
    result = _parse_kwargs({"all": None})  # ❌ Testing internal function
    assert list(result) == ["--all"]

# DO: Test through public API
def test_command_with_flag():
    result = COMMAND.git.commit(all=None)  # ✅ Testing public interface
    assert list(result) == ["git", "commit", "--all"]
```

The second test verifies that `_parse_kwargs` works correctly without coupling the test to the internal implementation.

### When This Philosophy Applies

- **Always** for this codebase
- When you're adding new tests
- When you're reviewing existing tests
- When you're refactoring code

### When to Ask Questions

If you notice:
- A public API isn't working as expected
- Missing test coverage for a public interface
- A need to verify edge cases through the public API

Then: **Write tests for the public interface that exercise those cases**, don't test the internals.

---

*This document ensures consistent testing practices and enables fearless refactoring.*
