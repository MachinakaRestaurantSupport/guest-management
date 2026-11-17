# ruff: noqa: E501
"""HTML UI router for guest-management."""

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from guest_management.store import InMemoryStore

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]

STATUS_META = {
    "available": ("空席（案内可）", "badge-ok", "#dcfce7"),
    "occupied": ("着席中（注文受付）", "badge-info", "#dbeafe"),
    "cleaning": ("清掃中（片付け待）", "badge-warn", "#fef3c7"),
}


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "guest" else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("tables", "座席ステータスマップ", "/ui/tables"),
        ("checkin", "来客受付・QR発行", "/ui/checkin"),
        ("guests", "会員ポイント・席清掃", "/ui/guests"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{ --bg:#f8fafc; --surface:#fff; --navy:#0f172a; --slate:#334155; --muted:#64748b; --border:#e2e8f0; --accent:#ea580c; --accent-soft:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--navy); line-height:1.5; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }}
    .topbar {{ background:var(--navy); color:#fff; padding:0 24px; height:54px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:15px; white-space:nowrap; }}
    .brand-badge {{ background:var(--accent); color:#fff; padding:2px 8px; border-radius:6px; font-size:11px; }}
    .nav-links {{ display:flex; gap:4px; overflow-x:auto; }}
    .nav-pill {{ color:#cbd5e1; text-decoration:none; font-size:12px; font-weight:600; padding:6px 10px; border-radius:6px; white-space:nowrap; }}
    .nav-pill.active {{ background:var(--accent); color:#fff; }}
    .subbar {{ background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .subbar h1 {{ margin:0; font-size:18px; }}
    .subbar .subtitle {{ margin:2px 0 0; font-size:12px; color:var(--muted); }}
    .subtabs {{ display:flex; gap:8px; }}
    .subtab {{ text-decoration:none; color:var(--slate); font-size:13px; font-weight:600; padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
    .subtab.active {{ background:var(--accent-soft); color:var(--accent); border-color:#fdba74; }}
    .container {{ max-width:1220px; margin:0 auto; padding:20px 24px 28px; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }}
    .table-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
    .grid-2 {{ display:grid; grid-template-columns:1.2fr 1fr; gap:18px; }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .kpi-label {{ font-size:12px; color:var(--muted); font-weight:600; }}
    .kpi-value {{ font-size:24px; font-weight:800; margin-top:4px; }}
    .badge {{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:11px; font-weight:700; }}
    .badge-ok {{ background:#dcfce7; color:#166534; }}
    .badge-info {{ background:#dbeafe; color:#1e40af; }}
    .badge-warn {{ background:#fef3c7; color:#92400e; }}
    .seat-card {{ border:1px solid var(--border); border-radius:12px; padding:14px; background:#fff; }}
    .btn {{ display:inline-block; text-decoration:none; font-size:12px; font-weight:700; padding:7px 13px; border-radius:8px; border:none; cursor:pointer; }}
    .btn-primary {{ background:var(--accent); color:#fff; }}
    .btn-secondary {{ background:#f1f5f9; color:var(--slate); border:1px solid var(--border); }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:10px 12px; background:#f8fafc; color:var(--muted); font-size:12px; border-bottom:1px solid var(--border); }}
    td {{ padding:10px 12px; border-bottom:1px solid var(--border); }}
    label {{ font-size:12px; font-weight:700; color:var(--slate); display:block; margin-bottom:4px; }}
    input, select {{ width:100%; padding:8px 10px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; font-family:inherit; }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def _qr_svg() -> str:
    return (
        '<svg width="96" height="96" viewBox="0 0 24 24" style="border:1px solid #cbd5e1;padding:6px;background:#fff;border-radius:8px">'
        '<rect x="1" y="1" width="7" height="7" fill="#0f172a"/><rect x="3" y="3" width="3" height="3" fill="#fff"/>'
        '<rect x="4" y="4" width="1" height="1" fill="#0f172a"/>'
        '<rect x="16" y="1" width="7" height="7" fill="#0f172a"/><rect x="18" y="3" width="3" height="3" fill="#fff"/>'
        '<rect x="19" y="4" width="1" height="1" fill="#0f172a"/>'
        '<rect x="1" y="16" width="7" height="7" fill="#0f172a"/><rect x="3" y="18" width="3" height="3" fill="#fff"/>'
        '<rect x="4" y="19" width="1" height="1" fill="#0f172a"/>'
        '<rect x="10" y="2" width="2" height="2" fill="#0f172a"/><rect x="12" y="6" width="2" height="4" fill="#0f172a"/>'
        '<rect x="9" y="10" width="5" height="2" fill="#0f172a"/><rect x="16" y="11" width="3" height="3" fill="#0f172a"/>'
        '<rect x="10" y="15" width="4" height="2" fill="#0f172a"/><rect x="16" y="17" width="6" height="5" fill="#0f172a"/>'
        "</svg>"
    )


def create_ui_router(store: InMemoryStore) -> APIRouter:
    """Create FastAPI router providing HTML UI screens for guest-management."""
    router = APIRouter(tags=["ui"])

    @router.get("/ui/tables", response_class=HTMLResponse)
    def table_map_page() -> str:
        tables = store.list_tables()
        avail = sum(1 for t in tables if t.status == "available")
        occ = sum(1 for t in tables if t.status == "occupied")
        clean = sum(1 for t in tables if t.status == "cleaning")

        cards = []
        for t in tables:
            label, badge_cls, tint = STATUS_META[t.status]
            session_info = (
                f"QRトークン: <code>{escape(t.qr_token[:10])}...</code>"
                if t.qr_token
                else "セッション未開始"
            )
            action = (
                '<a class="btn btn-primary" href="/ui/checkin">着席受付へ</a>'
                if t.status == "available"
                else (
                    '<a class="btn btn-secondary" href="/ui/guests">清掃完了へ</a>'
                    if t.status == "cleaning"
                    else '<span style="font-size:11px;color:#1e40af;font-weight:700">お食事中</span>'
                )
            )
            cards.append(
                f'<div class="seat-card" style="border-top:4px solid {tint}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<strong style="font-size:18px">席 {escape(t.table_number)}</strong>'
                f'<span class="badge {badge_cls}">{label}</span></div>'
                f'<div style="font-size:12px;color:#64748b;margin:6px 0">定員: {t.capacity} 名 ／ {session_info}</div>'
                f'<div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-size:11px;color:#94a3b8">ID: {escape(t.id[:8])}</span>{action}</div></div>'
            )
        cards_html = "".join(cards) or '<p style="color:#64748b">登録されている座席がありません。</p>'
        body = f"""
        <div class="kpi-grid">
          <div class="card"><div class="kpi-label">総座席数</div><div class="kpi-value">{len(tables)} 卓</div></div>
          <div class="card"><div class="kpi-label">空席（案内可能）</div><div class="kpi-value" style="color:#166534">{avail} 卓</div></div>
          <div class="card"><div class="kpi-label">着席中</div><div class="kpi-value" style="color:#1e40af">{occ} 卓</div></div>
          <div class="card"><div class="kpi-label">清掃待ち</div><div class="kpi-value" style="color:#92400e">{clean} 卓</div></div>
        </div>
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <h2 style="margin:0;font-size:16px">フロア座席リアルタイム状況</h2>
            <a class="btn btn-primary" href="/ui/checkin">＋ 来客受付・QR発行</a>
          </div>
          <div class="table-grid">{cards_html}</div>
        </div>
        """
        return _render_shell(
            title="顧客・座席管理 › 座席ステータスマップ",
            subtitle="店舗内すべてのテーブル（空席・着席中・清掃中）をリアルタイムで可視化します",
            active_subtab="tables",
            body_html=body,
        )

    @router.get("/ui/checkin", response_class=HTMLResponse)
    def checkin_page() -> str:
        tables = store.list_tables()
        avail_tables = [t for t in tables if t.status == "available"]
        occ_tables = [t for t in tables if t.status == "occupied"]
        target = occ_tables[0] if occ_tables else (tables[0] if tables else None)

        options = "".join(
            f'<option value="{escape(t.id)}">{escape(t.table_number)}（定員 {t.capacity}名）</option>'
            for t in avail_tables
        ) or '<option value="">空席がありません</option>'

        if target is not None:
            qr_panel = (
                f'<div style="display:flex;gap:16px;align-items:center">'
                f"{_qr_svg()}"
                f'<div><div style="font-weight:700;font-size:16px">席 {escape(target.table_number)} 用 注文QR</div>'
                f'<div style="font-size:12px;color:#475569;margin:4px 0">状態: {STATUS_META[target.status][0]}</div>'
                f'<div style="font-size:12px;color:#475569">Session: <code>{escape(target.current_session_id or "未発行")}</code></div>'
                f'<div style="font-size:12px;color:#475569">QR Token: <code>{escape(target.qr_token or "-")}</code></div></div></div>'
            )
        else:
            qr_panel = '<p style="color:#64748b">座席を先に登録してください。</p>'

        body = f"""
        <div class="grid-2">
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">新規来客の案内・着席セッション開始</h2>
            <div style="margin-bottom:12px">
              <label>案内する空席</label>
              <select id="c-table">{options}</select>
            </div>
            <div style="margin-bottom:12px">
              <label>来店人数（定員検証あり）</label>
              <input type="number" id="c-party" value="2" min="1">
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end">
              <a class="btn btn-secondary" href="/ui/tables">座席マップへ</a>
              <button class="btn btn-primary" onclick="occupyTable()">着席してQRトークン発行</button>
            </div>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">発行済みテーブルQRコード票</h2>
            {qr_panel}
            <div style="margin-top:14px;font-size:12px;color:#64748b;background:#f8fafc;padding:10px;border-radius:8px">
              お客様がこのQRコードを読み取ると <code>dine-in-ordering</code> 側でセッション認証され、テーブル注文が可能になります。
            </div>
          </div>
        </div>
        """ + """
        <script>
          async function occupyTable() {
            const tid = document.getElementById('c-table').value;
            if (!tid) return;
            const res = await fetch('/tables/' + tid + '/occupy', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({party_size: Number(document.getElementById('c-party').value)})
            });
            if (res.ok) { window.location.reload(); }
          }
        </script>
        """
        return _render_shell(
            title="顧客・座席管理 › 来客受付・QR発行",
            subtitle="来店人数の定員チェックを行い、着席セッションと店内注文用QRトークンを発行します",
            active_subtab="checkin",
            body_html=body,
        )

    @router.get("/ui/guests", response_class=HTMLResponse)
    def guests_and_cleaning_page() -> str:
        guests = store.list_guests()
        cleaning_tables = [t for t in store.list_tables() if t.status == "cleaning"]

        guest_rows = "".join(
            f"<tr>"
            f"<td><strong>{escape(g.name)}</strong></td>"
            f"<td>{escape(g.email or '-')}</td>"
            f'<td><span class="badge badge-ok" style="font-size:13px">{g.points} pt</span></td>'
            f'<td><button class="btn btn-secondary" onclick="addPoints(\'{escape(g.id)}\')">+10 pt 付与</button></td>'
            f"</tr>"
            for g in guests
        ) or '<tr><td colspan="4" style="text-align:center;color:#64748b">登録会員がいません。</td></tr>'

        clean_rows = "".join(
            f"<tr>"
            f"<td><strong>席 {escape(t.table_number)}</strong></td>"
            f'<td><span class="badge badge-warn">清掃中</span></td>'
            f'<td><button class="btn btn-primary" onclick="releaseTable(\'{escape(t.id)}\')">清掃完了 → 空席に戻す</button></td>'
            f"</tr>"
            for t in cleaning_tables
        ) or '<tr><td colspan="3" style="text-align:center;color:#64748b">現在清掃待ちの座席はありません。</td></tr>'

        body = f"""
        <div class="grid-2">
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">会員顧客・ポイント管理</h2>
            <table>
              <thead><tr><th>会員名</th><th>メール</th><th>保有ポイント</th><th>操作</th></tr></thead>
              <tbody>{guest_rows}</tbody>
            </table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">会計後の清掃完了・席再利用切替（I-6）</h2>
            <table>
              <thead><tr><th>座席</th><th>状態</th><th>操作</th></tr></thead>
              <tbody>{clean_rows}</tbody>
            </table>
          </div>
        </div>
        """ + """
        <script>
          async function addPoints(gid) {
            const res = await fetch('/guests/' + gid + '/points', {
              method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({delta: 10})
            });
            if (res.ok) window.location.reload();
          }
          async function releaseTable(tid) {
            const res = await fetch('/tables/' + tid + '/release', {method: 'POST'});
            if (res.ok) window.location.reload();
          }
        </script>
        """
        return _render_shell(
            title="顧客・座席管理 › 会員ポイント・席清掃完了",
            subtitle="会計後の会員ポイント付与および清掃完了による席の再利用切替を行います",
            active_subtab="guests",
            body_html=body,
        )

    return router
