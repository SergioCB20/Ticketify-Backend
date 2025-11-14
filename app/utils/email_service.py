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


# Instancia global del servicio
email_service = EmailService()
