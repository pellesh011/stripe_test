import { useEffect, useState } from "react";
import { getActiveCart } from "../api/cart.js";
import { formatPrice } from "../api/products.js";

export default function CartPage({ onBackToProducts }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getActiveCart()
      .then((result) => {
        if (!cancelled) setCart(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <p className="app__status">Загрузка…</p>;
  }

  if (error) {
    return <p className="app__status app__status--error">Ошибка: {error}</p>;
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="page">
        <p className="app__status">Корзина пуста</p>
        <div className="page__actions">
          <button
            type="button"
            className="button"
            onClick={onBackToProducts}
          >
            К товарам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2 className="page__title">Корзина</h2>
      <div className="cart">
        {cart.items.map((item) => (
          <div className="cart__item" key={item.id}>
            <span className="cart__item-name">{item.product_name}</span>
            <span className="cart__item-price">
              {formatPrice(item.price, item.currency)}
            </span>
          </div>
        ))}
      </div>
      <div className="page__actions">
        <button
          type="button"
          className="button"
          onClick={onBackToProducts}
        >
          К товарам
        </button>
      </div>
    </div>
  );
}