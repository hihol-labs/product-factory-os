# Premium Packs

Premium packs are paid starter/template packs built on top of the open source runtime.

Initial candidates:

- Pro SaaS with auth, billing, admin, onboarding, analytics
- Telegram bot with CRM and notifications
- AI agent SaaS
- Marketplace starter
- Scraper with queues, proxies, monitoring

Premium packs must still pass the open-source runtime contract:

- starter metadata validates;
- `pfo new -> pfo plan -> pfo validate` works;
- route snapshots or golden-path coverage exist;
- `.pfo/` contracts remain project-owned and visible to the user.
