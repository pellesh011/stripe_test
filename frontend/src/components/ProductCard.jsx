import { useMemo } from "react";
import { formatPrice } from "../api/products.js";

export default function ProductCard({ product, onBuyOneClick }) {
  const price = product.prices?.[0] ?? null;

  const priceLabel = useMemo(
    () => (price ? formatPrice(price.price, price.currency) : "—"),
    [price]
  );

  return (
    <div className="card">
      <h2 className="card__name">{product.name}</h2>
      <p className="card__price">{priceLabel}</p>
      <button
        type="button"
        className="card__buy"
        disabled={!price}
        onClick={() => onBuyOneClick(product)}
      >
        Купить в один клик
      </button>
    </div>
  );
}
