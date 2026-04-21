from src.admin_panel import ServiceAccount


def get_account_with_minimum_loaded(accounts) -> ServiceAccount:
    stats = [(account, len(account.groups.all())) for account in accounts]
    return min(
        stats,
        key=lambda item: (item[1], item[0].name)
    )[0]


def get_accounts_with_minimum_and_maximum_loaded(accounts):
    stats = [(account, len(account.groups.all())) for account in accounts]
    return (min(stats, key=lambda item: (item[1], item[0].name))[0],
            max(stats, key=lambda item: (item[1], item[0].name))[0])
