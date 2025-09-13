const Engine = (() => {
  const state = {
    owner: "Facilitairinfo",
    repo: "Newsfeeds",
    branch: "main",
    proxyURL: "https://your-worker.cloudflare.workers.dev", // <-- Vervang dit
    token: null,
  };

  function setToken(t) {
    state.token = t;
    if (t) localStorage.setItem("sloth_token", t);
  }

  function loadToken() {
    const t = localStorage.getItem("sloth_token");
    if (t) state.token = t;
    return state.token;
  }

  async function githubGet(path) {
    const res = await fetch(`https://api.github.com/repos/${state.owner}/${state.repo}/${path}`, {
      headers: {
        Authorization: `Bearer ${state.token}`,
        Accept: "application/vnd.github+json",
      },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function githubPutFile(targetPath, contentText, message) {
    const getPath = `contents/${encodeURIComponent(targetPath)}?ref=${state.branch}`;
    let sha = undefined;
    try {
      const existing = await githubGet(getPath);
      sha = existing.sha;
    } catch (_) {}
    const body = {
      message: message || `Update ${targetPath}`,
      content: btoa(unescape(encodeURIComponent(contentText))),
      branch: state.branch,
      sha,
    };
    const res = await fetch(`https://api.github.com/repos/${state.owner}/${state.repo}/contents/${encodeURIComponent(targetPath)}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${state.token}`,
        Accept: "application/vnd.github+json",
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function fetchSnapshot(url) {
    const res = await fetch(`${state.proxyURL}/?url=${encodeURIComponent(url)}`);
    if (!res.ok) throw new Error("Proxy fetch failed");
    return await res.text();
  }

  return { state, setToken, loadToken, githubPutFile, fetchSnapshot };
})();
