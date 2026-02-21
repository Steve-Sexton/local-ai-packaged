import unittest

from start_services import _toggle_searxng_cap_drop


COMPOSE_FIXTURE = """services:
  open-webui:
    cap_drop:
      - ALL

  searxng:
    container_name: searxng
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
"""


class TestStartServices(unittest.TestCase):
    def test_toggle_disables_cap_drop_only_for_searxng(self):
        updated, changed = _toggle_searxng_cap_drop(COMPOSE_FIXTURE, disable=True)

        self.assertTrue(changed)
        self.assertIn("  open-webui:\n    cap_drop:\n      - ALL", updated)
        self.assertIn("  searxng:\n    container_name: searxng\n    # cap_drop:\n    #   - ALL  # Temporarily commented out for first run", updated)

    def test_toggle_restores_cap_drop(self):
        disabled, _ = _toggle_searxng_cap_drop(COMPOSE_FIXTURE, disable=True)
        updated, changed = _toggle_searxng_cap_drop(disabled, disable=False)

        self.assertTrue(changed)
        self.assertIn("  searxng:\n    container_name: searxng\n    cap_drop:\n      - ALL", updated)

    def test_toggle_handles_windows_crlf_line_endings(self):
        crlf_fixture = COMPOSE_FIXTURE.replace("\n", "\r\n")

        disabled, changed = _toggle_searxng_cap_drop(crlf_fixture, disable=True)
        self.assertTrue(changed)
        self.assertIn("  open-webui:\r\n    cap_drop:\r\n      - ALL", disabled)
        self.assertIn(
            "  searxng:\r\n    container_name: searxng\r\n    # cap_drop:\r\n    #   - ALL  # Temporarily commented out for first run",
            disabled,
        )

        restored, changed = _toggle_searxng_cap_drop(disabled, disable=False)
        self.assertTrue(changed)
        self.assertIn("  searxng:\r\n    container_name: searxng\r\n    cap_drop:\r\n      - ALL", restored)


if __name__ == "__main__":
    unittest.main()
