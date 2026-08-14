export async function getActiveCart() {
  const response = await fetch("/api/cart/");
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  const data = await response.json();
  return data.cart || null;
}

export async function addToCart(productId, productPriceId, cartId) {
  const response = await fetch("/api/cart/add/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: productId,
      product_price_id: productPriceId,
      cart_id: cartId,
    }),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.error || `API error: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return data.cart || null;
}

export async function checkoutCart(cartId, currency, discount) {
  const body = {
    cart_id: cartId,
    currency,
  };
  if (discount) {
    body.discount = discount;
  }
  const response = await fetch("/api/cart/checkout/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.error || `API error: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return data;
}