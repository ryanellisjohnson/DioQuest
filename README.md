# DioQuest website

A static rebuild of www.dioquest.com. No framework and no dependencies beyond Python 3.

## Layout

| Path | What it is |
| --- | --- |
| `src/pages/` | One file per page: a short header block (title, description, URL path) followed by that page's HTML. |
| `src/layout.html` | The shared shell: `<head>`, header/navigation and footer wrapped around every page. |
| `src/assets/` | Stylesheet (`css/site.css`), script (`js/site.js`) and images (`img/`). |
| `build.py` | Turns `src/` into the finished site in `public/`. Also holds the site settings. |
| `public/` | **Generated — do not edit by hand.** This folder is what gets uploaded to the web host. |

## Making a change

1. Edit the file in `src/`.
2. Rebuild:

   ```bash
   python3 build.py
   ```

3. Preview at http://localhost:8765:

   ```bash
   python3 -m http.server 8765 --directory public
   ```

To add a news article, copy one of the files in `src/pages/news/`, change its header block and text, then add a card for it to `src/pages/news.html` (and to the home page if it should be featured).

## Settings (top of `build.py`)

- `SITE_URL` — the public address, used for canonical links and the sitemap.
- `CONTACT_EMAIL` — the address shown on the contact page, in the footer and
  behind the store's "Email to request" buttons.
- `REDIRECTS` — old Squarespace addresses (product pages, cart) that forward to
  their new homes.

## Publishing (Vercel)

The site is set up for Vercel. `vercel.json` tells Vercel to run `build.py` and
serve the `public/` folder, so `public/` is never uploaded or committed —
Vercel rebuilds it from `src/` on every deploy.

**Option A — from GitHub (recommended).** Put this folder in a GitHub
repository, then in Vercel choose *Add New → Project* and import that
repository. No settings need changing. After that, every push to the main
branch publishes the site, and every other branch gets its own preview address.

**Option B — from this computer.** With Node.js installed:

```bash
npx vercel
```

publishes a preview at a temporary address (the first run asks you to sign in
and name the project), and

```bash
npx vercel --prod
```

publishes to the live address.

**Connecting www.dioquest.com.** In the Vercel project, open *Settings →
Domains*, add `www.dioquest.com` and `dioquest.com`, and make the DNS changes
Vercel lists at your domain registrar. The Squarespace site stays live until
those DNS records change, so check the Vercel preview address first.

Page addresses match the old site (`/about`, `/news`, `/contact`, `/store`, and
both news article URLs), so existing links keep working. Vercel serves
`404.html` for missing pages.

## Differences from the Squarespace site

- The store is a catalogue: each "Email to request" button starts an email to
  us with the panel named in the subject. There is no cart or online payment.
- There is no contact form. The contact page gives the email address and
  postal address instead.
- Images were saved from the Squarespace CDN in WebP format at up to 1500px wide.
