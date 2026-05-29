# Monorepo Documentation

Este directorio contiene la documentación global del monorepo.

## Componentes del Proyecto:
- **Frontend**: Aplicación del lado cliente en Node.js.
- **Backend**: API REST en Node.js.
- **Infraestructura**: Declaración de infraestructura como código utilizando Terraform (Mock).

## Políticas del CI/CD:
- Los cambios realizados únicamente en este directorio (`documentación/`) no dispararán las pruebas de código ni de infraestructura, ahorrando recursos del runner.
Prueba de funcionamiento actions
