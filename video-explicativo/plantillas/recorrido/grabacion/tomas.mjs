// Lo PROPIO de cada app: qué se hace en cada toma. grabar.mjs (el motor) no se toca.
//
// Una toma = una sesión de navegador que graba varias escenas seguidas (una por línea del guion, mismo id).
// Dentro de una escena, aPalabra("x") espera hasta que la voz dice «x» (o a(f), la fracción f de su voz): la acción cae
// sobre la palabra que la nombra.
// Las cargas lentas y los precalentamientos (3D, mapas) van FUERA de escena(): el montaje los corta.
// Toda acción que pueda fallar va en intento(): si falla, la escena sigue y queda en grabar.log.
//
// Este ejemplo graba la app de demostración de la skill (pruebas/app-demo, servida en 127.0.0.1:4321).

// Se corre una vez al abrir el navegador, antes de la toma: sesión, datos sembrados, precalentar.
// Sesión: entrar por el formulario con una cuenta de EJEMPLO cuyas credenciales vienen del entorno (nunca se imprimen):
//   const { page } = h;  await h.ir("/entrar");  await page.getByLabel("Correo").fill(process.env.VIDEO_USUARIO);
//   await page.getByLabel("Contraseña").fill(process.env.VIDEO_CLAVE);  await page.getByRole("button", { name: "Entrar" }).click();
//   await page.waitForURL((u) => !u.pathname.startsWith("/entrar"));
// La cookie queda en el contexto para toda la toma. (Por http, una cookie `Secure` no viaja: usar la copia local sin Secure.)
export async function preparar(h) {
  void h;
}

export default {
  async tablero({ page, ir, escena, a, aPalabra, intento, señalar, clic, escribir, foco, moverA }) {
    await ir("/", 1200);
    await escena("t1", async () => {
      await a(0.1); await señalar(page.locator("h1"));
      await aPalabra("pedidos"); await foco(page.locator("#k-pedidos"), { seg: 3, zoom: 1.4 });
      await aPalabra("despachados"); await intento("despachados", () => señalar(page.locator("#k-listos")));
    });
    await escena("t2", async () => {
      await aPalabra("toque"); await clic(page.getByRole("button", { name: "Nuevo pedido" }), 300);
      await aPalabra("cliente"); await escribir(page.getByLabel("Cliente"), "Café Sur", 40);
      await aPalabra("después"); await escribir(page.getByLabel("Producto"), "Pan × 4", 40);
      await aPalabra("final"); await clic(page.getByRole("button", { name: "Guardar pedido" }), 300);
    });
    await escena("t3", async () => {
      await a(0.1); await foco(page.locator("#filas tr").first(), { seg: 2.5, zoom: 1.3 });
      await a(0.6); await intento("contador", () => foco(page.locator("#k-pedidos"), { seg: 2.2, zoom: 1.5, anillo: false }));
      await moverA(800, 700, 600);
    });
  },
};
