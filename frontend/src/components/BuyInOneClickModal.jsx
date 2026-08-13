import { useState } from "react";
import { CURRENCY_LABELS } from "../api/products.js";

const CURRENCIES = ["usd", "rub", "eur"];

export default function BuyInOneClickModal({ product, price, onClose, onSubmit }) {
  const [currency, setCurrency] = useState(price?.currency ?? "usd");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!price) return;
    setLoading(true);
    setError(null);
    try {
      await onSubmit(product.id, currency);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="modal" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="modal__panel" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal__title">Купить в один клик</h3>
        <p className="modal__product">{product.name}</p>

        <div className="modal__currencies">
          {CURRENCIES.map((cur) => (
            <button
              key={cur}
              type="button"
              className="modal__currency"
              data-active={currency === cur}
              onClick={() => setCurrency(cur)}
            >
              {CURRENCY_LABELS[cur]}
            </button>
          ))}
        </div>

        <p className="modal__price">
          {price
            ? `${price.price} ${CURRENCY_LABELS[price.currency]}`
            : "Цена недоступна"}
        </p>

        {error && <p className="modal__error">Ошибка: {error}</p>}

        <div className="modal__actions">
          <button
            type="button"
            className="modal__button"
            disabled={!price || loading}
            onClick={handleSubmit}
          >
            {loading ? "Оплата…" : "Оплатить"}
          </button>
          <button
            type="button"
            className="modal__button modal__button--secondary"
            onClick={onClose}
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  );
}
