"""
Servicio de envío de correos electrónicos para Ticketify
Soporta emails transaccionales con templates HTML
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import base64

class EmailService:
    """Servicio para enviar correos electrónicos"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Enviar un correo electrónico

        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            text_content: Contenido de texto plano (fallback)

        Returns:
            bool: True si se envió correctamente, False si hubo error
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Agregar contenido de texto plano (fallback)
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Agregar contenido HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Conectar y enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"✅ Email enviado a {to_email}: {subject}")
            return True

        except Exception as e:
            print(f"❌ Error al enviar email a {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, to_email: str, first_name: str) -> bool:
        """Enviar email de bienvenida después del registro"""
        subject = f"¡Bienvenido a {settings.APP_NAME}! 🎉"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%); padding: 40px 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 32px;">🎉 ¡Bienvenido!</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #1f2937; margin: 0 0 20px 0;">Hola {first_name},</h2>
                                    <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                                        ¡Tu cuenta en <strong>{settings.APP_NAME}</strong> ha sido creada exitosamente! 
                                        Estamos emocionados de tenerte con nosotros.
                                    </p>
                                    <div style="background-color: #f9fafb; border-left: 4px solid #a855f7; padding: 20px; margin: 20px 0;">
                                        <h3 style="color: #1f2937; margin: 0 0 15px 0; font-size: 18px;">¿Qué puedes hacer ahora?</h3>
                                        <ul style="color: #4b5563; line-height: 1.8; margin: 0; padding-left: 20px;">
                                            <li>Explora eventos increíbles cerca de ti</li>
                                            <li>Compra tickets de forma segura</li>
                                            <li>Vende tus tickets si no puedes asistir</li>
                                        </ul>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 0 30px 40px 30px; text-align: center;">
                                    <a href="http://localhost:3000" 
                                       style="display: inline-block; background-color: #a855f7; color: #ffffff; 
                                              padding: 14px 32px; text-decoration: none; border-radius: 6px; 
                                              font-weight: bold; font-size: 16px;">
                                        Explorar Eventos
                                    </a>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="color: #6b7280; font-size: 14px; margin: 0 0 10px 0;">
                                        Este es un correo automático, por favor no responder.
                                    </p>
                                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                        © {datetime.now().year} {settings.APP_NAME}. Todos los derechos reservados.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
        ¡Hola {first_name}!
        
        Bienvenido a {settings.APP_NAME}. Tu cuenta ha sido creada exitosamente.
        
        Ahora puedes:
        - Explorar eventos increíbles
        - Comprar tickets de forma segura
        - Vender tus tickets si no puedes asistir
        
        ¡Gracias por unirte a nosotros!
        
        El equipo de {settings.APP_NAME}
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_ticket_confirmation_email(
        self,
        to_email: str,
        first_name: str,
        event_title: str,
        event_date: str,
        event_venue: str,
        ticket_count: int,
        total_price: float
    ) -> bool:
        """Enviar email de confirmación de compra de tickets"""
        subject = f"¡Confirmación de tu compra en {settings.APP_NAME}! 🎫"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                            <tr>
                                <td style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 32px;">🎫 ¡Compra Confirmada!</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #1f2937; margin: 0 0 20px 0;">Hola {first_name},</h2>
                                    <p style="color: #4b5563; line-height: 1.6; margin: 0 0 30px 0;">
                                        ¡Tu compra ha sido procesada exitosamente! Aquí están los detalles:
                                    </p>
                                    <div style="border: 2px solid #e5e7eb; border-radius: 8px; padding: 24px; margin: 20px 0;">
                                        <h3 style="color: #a855f7; margin: 0 0 20px 0; font-size: 22px;">{event_title}</h3>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold; width: 40%;">📅 Fecha:</td>
                                                <td style="color: #1f2937;">{event_date}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold;">📍 Lugar:</td>
                                                <td style="color: #1f2937;">{event_venue}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold;">🎟️ Tickets:</td>
                                                <td style="color: #1f2937;">{ticket_count} ticket(s)</td>
                                            </tr>
                                            <tr style="border-top: 1px solid #e5e7eb;">
                                                <td style="color: #6b7280; font-weight: bold; padding-top: 16px;">💰 Total:</td>
                                                <td style="color: #10b981; font-size: 20px; font-weight: bold; padding-top: 16px;">
                                                    S/ {total_price:.2f}
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 0 30px 40px 30px; text-align: center;">
                                    <a href="http://localhost:3000/panel/my-tickets" 
                                       style="display: inline-block; background-color: #a855f7; color: #ffffff; 
                                              padding: 14px 32px; text-decoration: none; border-radius: 6px; 
                                              font-weight: bold; font-size: 16px;">
                                        Ver Mis Tickets
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
        ¡Hola {first_name}!
        
        Tu compra ha sido confirmada. Aquí están los detalles:
        
        Evento: {event_title}
        Fecha: {event_date}
        Lugar: {event_venue}
        Cantidad de tickets: {ticket_count}
        Total pagado: S/ {total_price:.2f}
        
        Tus tickets están disponibles en tu perfil.
        
        ¡Nos vemos en el evento!
        
        El equipo de {settings.APP_NAME}
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_test_email(self, to_email: str) -> bool:
        """Enviar email de prueba"""
        subject = f"Email de prueba - {settings.APP_NAME}"

        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #a855f7;">¡Email de prueba! 🧪</h2>
                <p>Este es un email de prueba del sistema de correos de Ticketify.</p>
                <p>Si estás recibiendo esto, ¡significa que el sistema funciona correctamente! ✅</p>
                <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                    Este es un correo automático, por favor no responder.
                </p>
            </body>
        </html>
        """

        text_content = "Este es un email de prueba del sistema de correos de Ticketify."

        return self.send_email(to_email, subject, html_content, text_content)

    def send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        attachments: list  # cada item: {cid, filename, content(base64)}
    ) -> bool:
        """
        Enviar correo con soporte para:
        - HTML
        - Texto plano
        - Imágenes inline (QR) vía CID
        - Adjuntos
        """
        try:
            msg = MIMEMultipart('related')  # necesario para inline images
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Parte alternativa (text + html)
            alternative_part = MIMEMultipart('alternative')

            if text_content:
                text_part = MIMEText(text_content, 'plain')
                alternative_part.attach(text_part)

            html_part = MIMEText(html_content, 'html')
            alternative_part.attach(html_part)

            msg.attach(alternative_part)

            # Procesar adjuntos (imágenes QR)
            for att in attachments:
                img_data = base64.b64decode(att["content"])
                img = MIMEImage(img_data, name=att["filename"])
                img.add_header('Content-ID', f"<{att['cid']}>")
                img.add_header('Content-Disposition', 'inline', filename=att["filename"])
                msg.attach(img)

            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"✅ Email enviado a {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error al enviar email a {to_email}: {str(e)}")
            return False

    def send_ticket_email(
        self,
        to_email: str,
        first_name: str,
        event_title: str,
        event_date: str,
        event_venue: str,
        tickets: list  # [{"id": "...", "qrCode": "...", "price": 35.0}, ...]
    ) -> bool:
        """Enviar correo con los tickets y sus códigos QR"""

        subject = f"🎟 Tus tickets para {event_title} están listos"

        # -------- Construir el HTML para los tickets ----------
        tickets_html = ""
        attachments = []

        for t in tickets:
            ticket_id = t["id"]
            qr_base64 = t["qrCode"]

            # Limpiar base64 (remover "data:image/png;base64,")
            base64_clean = qr_base64.split(",", 1)[1]

            # Agregar inline-img por CID
            cid = f"ticketqr-{ticket_id}"

            tickets_html += f"""
            <div style="border:1px solid #e5e7eb; padding:20px; border-radius:12px; margin-bottom:15px;">
                <h3 style="margin:0 0 10px 0;">Ticket #{ticket_id}</h3>
                <p style="margin:0 0 10px 0;">Precio: <strong>S/ {t['price']}</strong></p>

                <img
                    src="cid:{cid}"
                    alt="Código QR del Ticket"
                    style="width:200px; height:200px; border-radius:8px; border:1px solid #ccc;"
                />
            </div>
            """

            # Agregar como adjunto
            attachments.append({
                "cid": cid,
                "filename": f"ticket-{ticket_id}.png",
                "content": base64_clean
            })

        # -------- HTML del correo ----------
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background:#f3f4f6; padding:30px;">
            <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:12px;">

                <h2 style="color:#a855f7; margin-top:0;">🎫 ¡Aquí están tus tickets, {first_name}!</h2>

                <p style="color:#374151;">
                    Gracias por tu compra. Hemos preparado tus tickets para el evento:
                </p>

                <div style="background:#f9fafb; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="margin:0;"><strong>🎉 {event_title}</strong></p>
                    <p style="margin:0;">📅 {event_date}</p>
                    <p style="margin:0;">📍 {event_venue}</p>
                </div>

                <h3 style="color:#4b5563;">Tus Tickets:</h3>
                {tickets_html}

                <p style="color:#6b7280; font-size:12px; margin-top:40px;">
                    Este es un correo automático. No responder.
                </p>
            </div>
        </body>
        </html>
        """

        # Texto plano alternativo
        text_content = "Tus tickets están listos. Revisa la versión HTML para ver los QR."

        # -------- Llamar al método mejorado send_email --------
        return self.send_email_with_attachments(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments
        )

    def send_new_event_notification(
        self,
        to_email: str,
        first_name: str,
        event_title: str,
        event_description: str,
        category_name: str,
        event_date: str,
        event_location: str,
        event_url: str
    ) -> bool:
        """Enviar notificación de nuevo evento en categoría favorita"""
        subject = f"¡Nuevo evento de {category_name}! 🎉 - {event_title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%); padding: 40px 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 32px;">🎉 ¡Nuevo Evento!</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #1f2937; margin: 0 0 20px 0;">Hola {first_name},</h2>
                                    <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                                        ¡Hay un nuevo evento en tu categoría favorita <strong style="color: #a855f7;">{category_name}</strong>!
                                    </p>
                                    <div style="border: 2px solid #e5e7eb; border-radius: 8px; padding: 24px; margin: 20px 0; background-color: #f9fafb;">
                                        <h3 style="color: #a855f7; margin: 0 0 16px 0; font-size: 24px;">{event_title}</h3>
                                        <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                                            {event_description if len(event_description) < 200 else event_description[:200] + '...'}
                                        </p>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold; width: 30%;">📅 Fecha:</td>
                                                <td style="color: #1f2937;">{event_date}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold;">📍 Lugar:</td>
                                                <td style="color: #1f2937;">{event_location}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #6b7280; font-weight: bold;">🏷️ Categoría:</td>
                                                <td style="color: #a855f7; font-weight: bold;">{category_name}</td>
                                            </tr>
                                        </table>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 0 30px 40px 30px; text-align: center;">
                                    <a href="{event_url}"
                                       style="display: inline-block; background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
                                              color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 8px;
                                              font-weight: bold; font-size: 16px; margin-top: 10px;">
                                        Ver Evento
                                    </a>
                                    <p style="color: #6b7280; font-size: 14px; margin: 20px 0 0 0;">
                                        ¡No te pierdas esta oportunidad! Los cupos son limitados.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="color: #6b7280; font-size: 14px; margin: 0 0 10px 0;">
                                        Recibiste este correo porque tienes <strong>{category_name}</strong> como categoría favorita.
                                    </p>
                                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                        Puedes gestionar tus preferencias en tu perfil.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #1f2937; padding: 30px; text-align: center;">
                                    <p style="color: #9ca3af; font-size: 14px; margin: 0 0 10px 0;">
                                        © 2025 {settings.APP_NAME}. Todos los derechos reservados.
                                    </p>
                                    <p style="color: #6b7280; font-size: 12px; margin: 0;">
                                        Este es un correo automático, por favor no responder.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
        ¡Hola {first_name}!

        Hay un nuevo evento en tu categoría favorita {category_name}:

        {event_title}
        {event_description[:200] if len(event_description) > 200 else event_description}

        📅 Fecha: {event_date}
        📍 Lugar: {event_location}
        🏷️ Categoría: {category_name}

        Ver evento: {event_url}

        ¡No te pierdas esta oportunidad!

        El equipo de {settings.APP_NAME}
        """

        return self.send_email(to_email, subject, html_content, text_content)


# Instancia global del servicio
email_service = EmailService()
