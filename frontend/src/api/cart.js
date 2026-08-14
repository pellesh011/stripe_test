export async function getActiveCart() {
  const response = await fetch("/api/cart/");
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  const data = await response.json();
  return data.cart || null;
}