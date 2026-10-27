# Preguntas frecuentes

**¿Por qué un `escaped` no siempre significa una vulnerabilidad?**
Cada escape recibe un [reading](../concepts/results.md#readings): `confirmed`, un límite
documentado, una decisión de diseño, una dependencia de la plataforma o un supuesto del
contract que no se cumple para ese sandbox. Solo `confirmed` es un hallazgo.

**¿Por qué solo Linux?**
La imagen del lab y los runs publicados son Linux (kernel 6.8, Landlock ABI 4). Los runs en
macOS vienen después. Un contract lista en `os` los sistemas a los que aplica.

**¿Puedo confiar en un resultado de un sandbox que mantiene el autor?**
Revísalo. Cada caso tiene su evidencia cruda, los contracts vienen de las suites de tests de
otros proyectos y el corpus se versiona por hash, así que un contract cambiado para
acomodar un resultado aparece como una versión nueva
([Versiones del corpus](../concepts/corpus-versions.md)).

**Encontré una debilidad en un sandbox con un contract. ¿Dónde la reporto?**
Primero al proyecto de ese sandbox. Mira [`SECURITY.md`](repo:SECURITY.md).

**¿Cómo consigo que midan mi sandbox?**
Escribe su adapter ([Agregar un sandbox](../how-to/add-a-sandbox.md)) y abre un pull request,
o abre un issue pidiéndolo.
