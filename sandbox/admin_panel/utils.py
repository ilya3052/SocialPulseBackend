from admin_panel.models import ServiceAccount


def get_account_with_minimum_loaded(accounts) -> ServiceAccount:
    stats = [(account, len(account.groups.all())) for account in accounts]
    return min(
        stats,
        key=lambda item: (item[1], item[0].name)
    )[0]