import { CURRENCY_LABELS } from "../api/products.js";

export default function Header({
  view,
  onNavigate,
  currency,
  onCurrencyChange,
  cartItemCount,
}) {
  const currencies = Object.keys(CURRENCY_LABELS);

  return (
    <header className="header">
      <button
        type="button"
        className="header__brand"
        onClick={() => onNavigate("products")}
      >
        Магазин
      </button>

      <div className="header__actions">
        <div className="header__currencies">
          {currencies.map((cur) => (
            <button
              key={cur}
              type="button"
              className="header__currency"
              data-active={currency === cur}
              onClick={() => onCurrencyChange(cur)}
            >
              {CURRENCY_LABELS[cur]}
            </button>
          ))}
        </div>

        <nav className="header__nav">
          <button
            type="button"
            className="header__nav-button"
            data-active={view === "cart"}
            onClick={() => onNavigate("cart")}
          >
            Корзина
            {cartItemCount > 0 && (
              <span className="header__badge">{cartItemCount}</span>
            )}
          </button>
          <button
            type="button"
            className="header__nav-button"
            data-active={view === "orders"}
            onClick={() => onNavigate("orders")}
          >
            Заказы
          </button>
        </nav>
      </div>
    </header>
  );
}
