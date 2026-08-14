import { useState } from "react";
import { CURRENCY_LABELS } from "../api/products.js";

const CURRENCIES = ["usd", "rub", "eur"];

export default function CartCheckoutModal({ cart, onClose, onSubmit }) {
  const [currency, setCurrency] = useState("usd");
  const [discount, setDiscount] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await onSubmit(currency, discount.trim());
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="modal" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="modal__panel" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal__title">Оплатить заказ</h3>
        <p className="modal__product">Товаров: {cart.items.length}</p>

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

        <div className="modal__field">
          <label className="modal__label" htmlFor="cart-discount-input">
            Промокод
          </label>
          <input
            id="cart-discount-input"
            className="modal__input"
            type="text"
            value={discount}
            onChange={(e) => setDiscount(e.target.value)}
            placeholder="Необязательно"
          />
        </div>

        {error && <p className="modal__error">Ошибка: {error}</p>}

        <div className="modal__actions">
          <button
            type="button"
            className="modal__button"
            disabled={loading}
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