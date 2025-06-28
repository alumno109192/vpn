# Cambios de Iconos de Candado - VPN Manager

## Resumen
Se han actualizado todos los iconos de la aplicación VPN Manager para usar iconos de candado en lugar de iconos de red, proporcionando una representación visual más apropiada para una aplicación de seguridad VPN.

## Cambios Realizados

### 1. Icono Principal de la Bandeja del Sistema
- **Antes**: `QIcon.fromTheme("network-vpn")`
- **Después**: 
  - macOS: `QStyle.SP_FileDialogDetailedView`
  - Linux: `QIcon.fromTheme("security-high")`

### 2. Iconos de Estado de Conexión
- **Conectado**:
  - macOS: `QStyle.SP_DialogOkButton` (candado abierto/desbloqueado)
  - Linux: `QIcon.fromTheme("security-medium")`
- **Desconectado**:
  - macOS: `QStyle.SP_MessageBoxCritical` (candado cerrado/bloqueado)
  - Linux: `QIcon.fromTheme("security-low")`

### 3. Iconos de Menú
- **Submenús OpenVPN/IPsec**: Iconos de seguridad alta
- **Advertencias**: Iconos de advertencia de seguridad
- **Notificaciones**: Iconos de candado en mensajes del sistema

### 4. Compatibilidad Multiplataforma
- **macOS**: Usa iconos estándar de Qt Style (`QStyle.SP_*`)
- **Linux**: Usa iconos del tema del sistema (`QIcon.fromTheme()`)

## Archivos Modificados
- `Main.py`: Actualizado con todos los nuevos iconos de candado

## Funcionalidad Preservada
- Todos los estados de conexión mantienen su lógica
- Los tooltips y mensajes siguen funcionando
- La funcionalidad del menú contextual se mantiene intacta
- Los diferentes estados visuales siguen siendo distinguibles

## Estados Visuales del Candado
1. **Inicial/Neutral**: Candado estándar
2. **Conectado**: Candado abierto (verde/exitoso)
3. **Desconectado**: Candado cerrado (rojo/bloqueado)
4. **Advertencia**: Candado con símbolo de advertencia

## Beneficios
- Mejor representación visual de seguridad
- Iconos más intuitivos para usuarios
- Consistencia temática con aplicaciones de VPN
- Mantiene la funcionalidad completa existente

La aplicación ahora presenta un sistema coherente de iconos de candado que refleja mejor su propósito como herramienta de seguridad VPN.
