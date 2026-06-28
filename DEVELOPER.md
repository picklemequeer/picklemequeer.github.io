# Developer

This repo does 2 things:

1. deploys the static site, <https://picklemequeer.com>
2. generates HTML for the monthly email blast

## Local development

To view the email & landing page:

- Install [`uv`](https://github.com/astral-sh/uv)
- Install python packages with `uv`: `uv sync`
- Run `make render`
- Look at the output: `open index.html` or `open email.html`

That's it! `index.html` is for the static site (aka website, landing page, picklemequeer.com). `email.html` is for the email newsletter.

## Updating the site

- if you just need to update the schedule update the [finalized schedule google sheet](https://drive.google.com/drive/u/1/folders/1cArCeN1i7O01_ZfBKgub4tyg9-Yg5tqU) and the site will auto-update within 3 hours
- to test rendering different kinds of events locally, use `gameplay.csv` with `make render-local`
- to copy the google sheet to your local `gameplay.csv`, use `make fetch-csv`
- in addition to the above, the site will auto-deploy on every merge to `main`

## Sending emails

The email newsletter is managed through [Kit](https://app.kit.com/). If you're in the Discord organizing group, you'll know how to access credentials.

In Kit, there's a template, "PMQ Monthly", for the monthly newsletter. When sending the monthly email, go to broadcast, and use this template. Paste in the event specific HTML between the header and footer (i.e. run `make render` and look for the events part of `email.html`). Send a test broadcast to yourself to make sure nothings funky with the styling, and then to the broader subscriber population.

<https://picklemequeer.com> is managed through [Spaceship](https://www.spaceship.com/) and shouldn't need to be touched. If you need help, ask @mdzhang (@meesh in Discord)
<mailto:hi@picklemequeer.com> is setup to forward to <mailto:picklemequeer@gmail.com> using [ImprovMX](https://app.improvmx.com/). Again, if you're in the organizing group, you'll know how to access credentials.
