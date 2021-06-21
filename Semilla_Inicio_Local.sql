
DELETE FROM `pruebas`.`com_entradamercaderiadet`;

DELETE FROM `pruebas`.`com_entradamercaderiamsr`;

DELETE FROM `pruebas`.`com_ordencompradet`;

DELETE FROM `pruebas`.`com_ordencompramsr`;

DELETE FROM `pruebas`.`com_profordet`;

DELETE FROM `pruebas`.`com_proformamsr`;

DELETE FROM `pruebas`.`com_cotizaciondet`;

DELETE FROM `pruebas`.`com_cotizacionmsr`;

DELETE FROM `pruebas`.`com_proveedorcontacto`;

DELETE FROM `pruebas`.`com_proveedordireccion`;

DELETE FROM `pruebas`.`com_proveedor`;

DELETE FROM `pruebas`.`com_temprem`;

DELETE FROM `pruebas`.`vta_exorubrocliente`;

DELETE FROM `pruebas`.`vta_facturadet`;

DELETE FROM `pruebas`.`vta_facturamsr`;

DELETE FROM `pruebas`.`vta_instanciafactmsr`;

DELETE FROM `pruebas`.`vta_forma_pago`;

DELETE FROM `pruebas`.`vta_permisoscliente`;

DELETE FROM `pruebas`.`vta_proformadet`;

DELETE FROM `pruebas`.`vta_proformamsr`;

DELETE FROM `pruebas`.`vta_tempcombo`;

DELETE FROM `pruebas`.`vta_cliente_cooperativa`;

DELETE FROM `pruebas`.`vta_cooperativa`;

DELETE FROM `pruebas`.`vta_uniones`;

DELETE FROM `pruebas`.`vta_vendedores`;

DELETE FROM `pruebas`.`caja_registros`;

DELETE FROM `pruebas`.`caja_cajas`;

DELETE FROM `pruebas`.`caja_tipomovimiento`;

DELETE FROM `pruebas`.`caja_naturaleza`;

DELETE FROM `pruebas`.`caja_tipocambio`;

DELETE FROM `pruebas`.`vta_clientedireccion`;

DELETE FROM `pruebas`.`vta_clientedocumento`;

DELETE FROM `pruebas`.`vta_clientetelefono`;

DELETE FROM `pruebas`.`vta_clientevehiculo`;

DELETE FROM `pruebas`.`vta_clientevehiculocolor`;

DELETE FROM `pruebas`.`vta_cliente`;

DELETE FROM `pruebas`.`vta_membresia`;

DELETE FROM `pruebas`.`vta_condicion`;

DELETE FROM `pruebas`.`inv_ajustedet`;

DELETE FROM `pruebas`.`inv_ajustedettemp`;

DELETE FROM `pruebas`.`inv_ajustemsr`;

DELETE FROM `pruebas`.`inv_ajustetipo`;

DELETE FROM `pruebas`.`inv_existenciabodega`;

DELETE FROM `pruebas`.`inv_trasladodet`;

DELETE FROM `pruebas`.`inv_trasladodettemp`;

DELETE FROM `pruebas`.`inv_trasladomsr`;

DELETE FROM `pruebas`.`inv_devoluciondet`;

DELETE FROM `pruebas`.`inv_devoluciondettemp`;

DELETE FROM `pruebas`.`inv_devolucioncondicion`;

DELETE FROM `pruebas`.`inv_devolucionmsr`;

DELETE FROM `pruebas`.`inv_item_costo`;

DELETE FROM `pruebas`.`inv_item_costo_historico`;

DELETE FROM `pruebas`.`inv_kardex`;

DELETE FROM `pruebas`.`inv_tempcatalogo`;

DELETE FROM `pruebas`.`inv_tempcatalogomsr`;

DELETE FROM `pruebas`.`inv_bodega_item_costo`;

DELETE FROM `pruebas`.`inv_bodega_item_costo_historico`;

DELETE FROM `pruebas`.`inv_n4itemproduccion`;

DELETE FROM `pruebas`.`inv_bodega`;

DELETE FROM `pruebas`.`inv_sucursal_item_costo`;

DELETE FROM `pruebas`.`inv_sucursal_item_costo_historico`;

DELETE FROM `pruebas`.`inv_n4itemcombo`;

DELETE FROM `pruebas`.`inv_n4itemimagen`;

DELETE FROM `pruebas`.`inv_n4itemreceta`;

DELETE FROM `pruebas`.`inv_n4itemvencimiento`;

DELETE FROM `pruebas`.`inv_n4itemxprecio`;

DELETE FROM `pruebas`.`inv_n4item`;

DELETE FROM `pruebas`.`inv_n3producto_aplicacion`;

DELETE FROM `pruebas`.`inv_n3productoimagen`;

DELETE FROM `pruebas`.`inv_n3producto`;

DELETE FROM `pruebas`.`inv_n2familia`;

DELETE FROM `pruebas`.`inv_n1rubro`;

DELETE FROM `pruebas`.`inv_precio`;

DELETE FROM `pruebas`.`inv_sucursal_usuarios`;

DELETE FROM `pruebas`.`usuarios_loggedinuser`;

DELETE FROM `pruebas`.`inv_sucursal`;

DELETE FROM `pruebas`.`inv_marcaitem`;

DELETE FROM `pruebas`.`inv_modelovehiculo`;

DELETE FROM `pruebas`.`inv_marcavehiculo`;

DELETE FROM `pruebas`.`inv_tipovehiculo`;

DELETE FROM `pruebas`.`inv_centrocosto`;

DELETE FROM `pruebas`.`inv_um`;

DELETE FROM `pruebas`.`inv_estado`;

DELETE FROM `pruebas`.`inv_exorubro`;

DELETE FROM `pruebas`.`inv_exotipo`;




/*
select * from pruebas.inv_centrocosto;
*/
INSERT INTO `pruebas`.`inv_centrocosto` 
(`nombre`, `cuenta_contab`) 
VALUES 
('Informatica', '00010001');

/*
select * from pruebas.inv_sucursal;
select * from pruebas_com.inv_sucursal;
*/
INSERT INTO `pruebas`.`inv_sucursal` 
(`siglas`, `nombre`, `direccion`, `telefonos`, `encabezado`, `pie_pagina`, `serie`,`existencia`,`saldo`) 
VALUES 
('CE', 'Central', 'Ciudad Dario', '22897533', 'MultiComercial,C.P', 'Un lema para la sucursal',  'B','0','0'),
('DU', 'Sin Sucursal', 'No tiene Direccion', '2222-1515', 'Encabezado estandar', 'Pie de Pagina Estadar', 'Z','0','0');
/*
select * from auth_user;
select * from inv_sucursal_usuarios;
select * from pruebas_com.inv_sucursal_usuarios;
*/
INSERT INTO `pruebas`.`inv_sucursal_usuarios` 
( `sucursal_id`, `user_id`) 
VALUES 
( 'CE', '1');
 
/*
select * from pruebas.inv_um;
select * from pruebas_com.inv_um;
*/
INSERT INTO `pruebas`.`inv_um` 
(`id_um`, `nombre`) 
VALUES 
('UNI', 'Unidad');

/*
select * from pruebas.inv_marcaitem;
select * from pruebas_com.inv_marcaitem;
*/
INSERT INTO `pruebas`.`inv_marcaitem` 
(`siglas`, `marca`) 
VALUES 
('GEN', 'GENERICA');

/*
select  * from pruebas.inv_marcavehiculo;
select  * from pruebas_com.inv_marcavehiculo;
*/
INSERT INTO `pruebas`.`inv_marcavehiculo` 
(`siglas`, `marca`) 
VALUES 
('NE', 'GENERICO');

/*
select  * from pruebas.inv_tipovehiculo;
select  * from pruebas_com.inv_tipovehiculo;
*/
INSERT INTO `pruebas`.`inv_tipovehiculo` 
(`id`, `descripcion`) 
VALUES 
('1', 'N/E');

/*
select  * from pruebas.inv_modelovehiculo;
select  * from pruebas_com.inv_modelovehiculo;
*/
/*INSERT INTO `pruebas`.`inv_modelovehiculo` (`id_modelo`, `modelo`, `cilindraje`, `combustible`, `anyo`, `marca_id`, `tipo_id`) VALUES ('NE.NEE000-0000', 'NO ESPECIFICA', '0.5', 'G', '1999', 'NE', '1');*/

INSERT INTO `pruebas`.`inv_modelovehiculo` 
(`id_modelo`, `modelo`, `cilindraje`, `combustible`, `anyo`, `marca_id`, `tipo_id`) 
VALUES 
('NE.NEE000', 'NO ESPECIFICA', '0.5', 'G', '1999', 'NE', '1');

/*
select * from pruebas.inv_devolucioncondicion;
select * from pruebas_com.inv_devolucioncondicion;
*/
INSERT INTO `pruebas`.`inv_devolucioncondicion` 
(`id`, `descripcion`, `valor`) 
VALUES 
('1', 'Bueno', '100'),
('2', 'Regular', '70'),
('3', 'Por definir', '70');


/*
select * from pruebas.inv_estado;
select * from pruebas_com.inv_estado;
*/
INSERT INTO `pruebas`.`inv_estado` 
(`id`, `estado_desc`) 
VALUES 
('1', 'Aprobado'),
('2', 'Anulado'),
('3', 'Autorizado'),
('4', 'Proceso'),
('5', 'En Espera'),
('6', 'Cerrado'),
('7', 'Devuelto'),
('8', 'Modificado'),
('9', 'Rechazado');

/*
select * from pruebas.inv_ajustetipo;
select * from pruebas_com.inv_ajustetipo;
*/
INSERT INTO `pruebas`.`inv_ajustetipo` 
(`id`, `tipo_mov`, `descripcion`) 
VALUES 
('1', 'S', 'Salida'),
('2', 'E', 'Entrada');


/*
select * from pruebas.inv_precio;
select * from pruebas_com.inv_precio;
*/
INSERT INTO `pruebas`.`inv_precio` 
(`id_precio`, `descripcion`) 
VALUES 
('A', 'Precio A'),
('B', 'Precio B'),
('C', 'Precio C');

/*
select * from pruebas.inv_bodega;
select * from pruebas_com.inv_bodega;
*/

INSERT INTO `pruebas`.`inv_bodega` 
(`id_bodega`, `siglas`, `nombre`, `tipo`, `sucursal_id`,`existencia`,`saldo`) 
VALUES 
('CETR', 'TR', 'Central TRANSITORIA', 'T', 'CE','0','0'),
('CETD', 'TD', 'Central TIENDA', 'F', 'CE','0','0'),
('CEDE', 'DE', 'Central DESPACHO', 'F', 'CE','0','0');


INSERT INTO `pruebas`.`inv_exorubro` 
(`id`,`nombre`, `unidades`, `costo`, `precio`) 
VALUES 
('1','SIN EXONERAR', '0', '0', '0');


/*
select * from pruebas.com_proveedor;
select * from pruebas_com.com_proveedor;
*/
INSERT INTO `pruebas`.`com_proveedor` 
(`abreviatura`, `nombre`, `ruc`, `web`, `comentario`) 
VALUES 
('EVE', 'Eventual', 'TRET', 'No posee', '.');

/*
select * from pruebas.inv_exotipo;
select * from pruebas_com.inv_exotipo;
*/
INSERT INTO `pruebas`.`inv_exotipo` 
(`id_exo`, `nombre`) 
VALUES 
('E', 'Excento'),
('G', 'Grabado'),
('X', 'Exonerable');

INSERT INTO `pruebas`.`caja_cajas` 
VALUES 
('CE01',1,9999,'CE');

INSERT INTO `pruebas`.`caja_naturaleza` 
VALUES 
('C','Cambios'),
('E','Entrada'),
('S','Salida');

INSERT INTO `pruebas`.`caja_tipocambio` VALUES 
(1,'2019-11-29',33.7,33.6,33.9),
(2,'2019-01-01',30.1,30,30.2),
(3,'2019-12-11',34,33.99,34.01);


INSERT INTO `pruebas`.`caja_tipomovimiento` 
VALUES 
('ED','Deposito','E'),
('EF','Factura','E'),
('ER','Recibos','E'),
('SD','Devolucion','S'),
('SR','Retiro','S');

INSERT INTO `pruebas`.`vta_membresia` 
VALUES 
(1,'particular/individual',0,0);

INSERT INTO `pruebas`.`vta_cliente` 
(`identificacion`, `nombres`, `apellidos`, `estado_civil`, `dependientes`, `limite_credito`, `saldo`, `tipo`, `magnetico`,`descuento`,`membresia_id`) 
VALUES 
('0','PARTICULAR','INDIVIDUAL','S',0,0.0000,0.00,'N','ASD','0','1');

INSERT INTO `pruebas`.`vta_uniones` 
(`id`, `nombre`) 
VALUES 
(1,'PARTICULAR');

INSERT INTO `pruebas`.`vta_cooperativa`
(`id`, `nombre`, `segmento`, `union_id`) 
VALUES 
('1','PARTICULAR/INDIVIDUAL','0',1);

/*La 2 es empleados sin exoneracion*/
INSERT INTO `pruebas`.`vta_cliente_cooperativa`(cliente_id,cooperativa_id) 
VALUES 
('0',1);

INSERT INTO `pruebas`.`vta_condicion` 
VALUES 
(1,'Contado'),
(2,'Credito');

INSERT INTO `pruebas`.`vta_forma_pago` 
VALUES 
(1,'Efectivo',1),
(2,'Tarjeta',1),
(3,'Credito',2);

INSERT INTO `pruebas`.`vta_vendedores` 
VALUES 
(1,'M','0000',1,'CE01');

INSERT INTO `pruebas`.`vta_facturamsr` 
(
 `referencia`, `serie`, `fechaemision`, `fechavencimiento`, `membresia`, `cooperativa`,
 `preciofinaltotal`, `descuentotal`, `extradescuento`, `impuestototal`, `impreso`, `cct`,
 `monto_cct`, `cliente_id`, `estado_id`, `formapago_id`, `sucursal_id`, `vendedor_id`
) 
VALUES 
(
 'DU-SV-001', 'Z0000000', '2020-04-22 16:35:25.165645', '2020-05-22', '1', '1',
 '0.0000', '0.0000', '0', '0.0000', '0', '0',
 '0', '0', '3', '2', 'CE', '1'
 );


INSERT INTO `pruebas`.`com_ordencompramsr` 
(
 `referencia`, `fecha`, `vencimiento`, `importado`, `recibido`, `tipo`,
 `moneda`, `condicion_id`, `estado_id`, `proveedor_id`
) 
VALUES 
(
 'DU-OC-19000101-01', '2020-04-21 15:51:05.503178', '2020-05-21', '0', '1', 'L',
 'C', '1', '3', 'EVE'
);


INSERT INTO `pruebas`.`com_entradamercaderiamsr` 
(
 `referencia`, `fecha`, `facturas`, `fecha_vencimiento`, `poliza`, `costo_compra`,
 `costo_iva`, `condicion_id`, `estado_id`, `ordenes_compra_id`, `proveedor_id`
) 
VALUES 
(
 'DU-EM-99999999-00001', '2020-04-21 15:51:58.904407', 'xxxxxx', '2020-04-21 15:51:58.903409', '0', '0',
 '0', '1', '3', 'DU-OC-19000101-01', 'EVE'
);












