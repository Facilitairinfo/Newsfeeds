function escapeXml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

function buildRSS({ title, link, description, items }) {
  const itemsXml = items.map(it => `
    <item>
      <title>${escapeXml(it.title)}</title>
      ${it.link ? `<link>${escapeXml(it.link)}</link>` : ""}
      ${it.pubDate ? `<pubDate>${escapeXml(it.pubDate)}</pubDate>` : ""}
      ${it.description ? `<description>${escapeXml(it.description)}</description>` : ""}
      ${it.guid ? `<guid isPermaLink="false">${escapeXml(it.guid)}</guid>` : ""}
    </item>`).join("");
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>${escapeXml(title)}</title>
<link>${escapeXml(link)}</link>
<description>${escapeXml(description)}</description>
${itemsXml}
</channel></rss>`;
}

function buildJSONFeed({ title, home_page_url, feed_url, items }) {
  return JSON.stringify({
    version: "https://jsonfeed.org/version/1",
    title,
    home_page_url,
    feed_url,
    items: items.map((it, idx) => ({
      id: it.guid || it.link || String(idx),
      url: it.link,
      title: it.title,
      content_text: it.description,
      date_published: it.pubDate,
    })),
  }, null, 2);
}
