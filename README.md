
# API de Pagos y Gestión de Niveles en Blockchain

## Información General

Esta API permite realizar pagos de comisiones y gestionar niveles en un contrato inteligente desplegado en la red de Ethereum (Polygon).

- **Base URL**: `https://<tu-dominio.com>/api`
- **Versión**: 1.0

## Autenticación

Para asegurar que solo sistemas autorizados puedan acceder a la API, todas las solicitudes deben incluir un token de autorización. El token debe ser enviado en el encabezado de la solicitud bajo la clave `Authorization` con el formato `Bearer <tu_token>`.

Por ejemplo, para autorizar una solicitud en Postman, añade un encabezado con `Key` como `Authorization` y `Value` como `Bearer 513c3cc4c10e446e7534ca21984c75ef`.

## Endpoints

### 1. Pagar Comisiones

- **URL**: `/pay_commissions`
- **Método**: `POST`
- **Descripción**: Realiza el pago de comisiones a múltiples direcciones de carteras en Ethereum.
- **Body** (application/json):

```json
{
  "wallets": ["0x...", "0x..."],
  "levels": [1, 2],
  "amount": "100"
}
```

- **Respuestas**:
  - **200 OK**:

    ```json
    {
      "status": 1,
      "transaction_hash": "<hash_de_la_transacción>",
      "url": "https://polygonscan.com/tx/<hash_de_la_transacción>"
    }
    ```

  - **500 Internal Server Error**:

    ```json
    {
      "status": "error",
      "message": "<mensaje_de_error>"
    }
    ```

### 2. Agregar Nivel

- **URL**: `/add_level`
- **Método**: `POST`
- **Descripción**: Agrega un nuevo nivel al contrato inteligente.
- **Body** (application/json):

```json
{
  "id": 3,
  "name": "Nivel Premium",
  "percent": 15
}
```

- **Respuestas**:
  - **200 OK**:

    ```json
    {
      "transaction_hash": "<hash_de_la_transacción>"
    }
    ```

  - **Error** (varía según el caso).

### 3. Obtener Balance del Contrato

- **URL**: `/getbalance`
- **Método**: `GET`
- **Descripción**: Obtiene el balance actual del contrato inteligente en Wei.
- **Respuestas**:
  - **200 OK**:

    ```json
    {
      "status": "success",
      "balance": "<balance_en_wei>"
    }
    ```

## Errores y Códigos de Estado

[Descripción general de cómo se manejan los errores y una lista de posibles códigos de estado HTTP y su significado.]

## Limitaciones y Cuotas

[Información sobre las limitaciones de la API, cuotas de uso, y cómo se manejan las solicitudes excesivas.]
