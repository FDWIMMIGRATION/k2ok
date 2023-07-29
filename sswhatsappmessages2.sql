USE whatsapp_messages;
SHOW TABLES;

/*pendiente ver si se limina*/
select * from largo_embeddings;
DELETE FROM largo_embeddings WHERE id >= 1;
ALTER TABLE largo_embeddings AUTO_INCREMENT = 1;
/*pendiente ver si se limina*/


select * from empl_usr_da;
OPTIMIZE TABLE empl_usr_da;

select * from tabla_formularios;

select * from medio_embeddings;
select * from histo_pregun;

# se pueden limpiar los datos
select * from agenda;
select * from area_envio;
select * from estado_usuario;
select * from mensajes_whatsapp;
select * from multimedia;
select * from orden_cliente;
select * from redirecion_cliente;
select * from tabla_cliente;

DELETE FROM agenda WHERE id >= 1;
DELETE FROM area_envio WHERE id >= 1;
DELETE FROM estado_usuario WHERE id >= 1;
DELETE FROM mensajes_whatsapp WHERE id >= 1;
DELETE FROM multimedia WHERE id >= 1;
DELETE FROM orden_cliente WHERE id >= 1;
DELETE FROM redirecion_cliente WHERE id >= 1;
DELETE FROM tabla_cliente WHERE id >= 1;

ALTER TABLE agenda AUTO_INCREMENT = 1;
ALTER TABLE area_envi AUTO_INCREMENT = 1;
ALTER TABLE estado_usuario AUTO_INCREMENT = 1;
ALTER TABLE mensajes_whatsapp AUTO_INCREMENT = 1;
ALTER TABLE multimedia AUTO_INCREMENT = 1;
ALTER TABLE orden_cliente AUTO_INCREMENT = 1;
ALTER TABLE redirecion_cliente AUTO_INCREMENT = 1;
ALTER TABLE tabla_cliente AUTO_INCREMENT = 1;

select * from tabla_formularios;
select * from tabla_cliente;

select * from medio_embeddings;

DELETE FROM medio_embeddings WHERE id >= 1;
ALTER TABLE medio_embeddings AUTO_INCREMENT = 1;

DELETE FROM histo_pregun WHERE id >= 1;
ALTER TABLE histo_pregun AUTO_INCREMENT = 1;

select * from histo_pregun;