import psycopg2
import sys

LOCAL_DB = "postgresql://zaragoza_user:zaragoza_pass@localhost:5432/zaragoza_historica"
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres"

def test():
    try:
        print("Probando conexión LOCAL...")
        conn_l = psycopg2.connect(LOCAL_DB)
        print("LOCAL OK.")
        conn_l.close()
        
        print("Probando conexión REMOTA (Supabase)...")
        conn_r = psycopg2.connect(REMOTE_DB)
        print("REMOTA OK.")
        conn_r.close()
        
    except Exception as e:
        print(f"Fallo detectado: {type(e).__name__}: {e}")
        # Intentar imprimir la representación cruda del error si falla el string
        try:
            print(f"Error crudo: {repr(e)}")
        except:
            pass

if __name__ == "__main__":
    test()
