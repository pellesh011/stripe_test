import { useMemo, useState } from "react";
import { formatPrice } from "../api/products.js";

export default function ProductCard({ product, onBuyOneClick, onAddToCart }) {
  const [added, setAdded] = useState(false);

  const price = product.prices?.[0] ?? null;

  const priceLabel = useMemo(
    () => (price ? formatPrice(price.price, price.currency) : "—"),
    [price]
  );

  const handleAddToCart = async () => {
    if (!price) return;
    try {
      await onAddToCart(product, price);
      setAdded(true);
      window.setTimeout(() => setAdded(false), 1500);
    } catch {
      // ошибка уже показана в App / корзине
    }
  };

  return (
    <div className="card">
      <h2 className="card__name">{product.name}</h2>
      <p className="card__price">{priceLabel}</p>
      <div className="card__actions">
        <button
          type="button"
          className="card__add"
          disabled={!price}
          onClick={handleAddToCart}
        >
          {added ? "Добавлено ✓" : "В корзину"}
        </button>
        <button
          type="button"
          className="card__buy"
          disabled={!price}
          onClick={() => onBuyOneClick(product, price)}
        >
          Купить в один клик
        </button>
      </div>
    </div>
  );
}