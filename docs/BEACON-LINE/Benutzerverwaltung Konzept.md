# Konzeptdokument: Vollständige Benutzerverwaltung mit cloudbasierter SQL-Datenbank auf Supabase

**Allgemeines Referenzdokument** · Version 2.0

---

## Inhaltsverzeichnis

1. [Einleitung und Zielsetzung](#1-einleitung-und-zielsetzung)
2. [Architekturüberblick](#2-architekturüberblick)
3. [Datenmodell](#3-datenmodell)
4. [Authentifizierungs-Flows](#4-authentifizierungs-flows)
5. [Sicherheitskonzept](#5-sicherheitskonzept)
6. [Rollen- und Rechtekonzept (RBAC)](#6-rollen--und-rechtekonzept-rbac)
7. [Datenschutz- und DSGVO-Aspekte](#7-datenschutz--und-dsgvo-aspekte)
8. [Zusammenfassung](#8-zusammenfassung)

---

## 1. Einleitung und Zielsetzung

Dieses Dokument beschreibt das Konzept einer vollständigen Benutzerverwaltung (User Management) für eine App, die auf Supabase als cloudbasierter SQL-Datenbank (PostgreSQL) aufsetzt. Es nutzt gezielt die Stärken von Supabase – den integrierten Auth-Service (GoTrue) sowie Row Level Security auf Postgres-Ebene – statt eine eigene Authentifizierungslogik nachzubauen.

Ziel ist es, alle Bausteine einer Benutzerverwaltung – von der Registrierung über Sessions und Rollen bis zu einem detaillierten Rechtekonzept und Datenschutz-Aspekten – in einer Form zu beschreiben, die sich direkt auf reale Supabase-Projekte übertragen lässt, unabhängig vom konkreten Frontend-Framework.

### 1.1 Geltungsbereich

Das Konzept deckt folgende Bereiche ab:

- Datenmodell (Tabellenstruktur) für Benutzer, Profile, Sessions und Rollen in Supabase
- Authentifizierungs-Flows (Registrierung, Login, Logout, Passwort-Reset) über Supabase Auth
- Token- und Session-Strategie
- Ausführliches Rollen- und Rechtekonzept (RBAC) mit konkreten RLS-Policies
- Sicherheitsmaßnahmen (Hashing, Rate Limiting, Row Level Security)
- Datenschutz- und DSGVO-relevante Aspekte

---

## 2. Architekturüberblick

Im Kern besteht die Benutzerverwaltung aus drei Schichten:

1. **Client** (App/Frontend) – sendet Anmeldedaten, hält das aktuelle Session-Token
2. **Supabase Auth (GoTrue)** – prüft Zugangsdaten, stellt Tokens aus, verwaltet Sessions
3. **Postgres-Datenbank** – speichert Benutzerdaten, Profile, Rollen und Audit-Informationen dauerhaft

### 2.1 Supabase Auth (GoTrue)

Supabase liefert mit GoTrue einen fertigen Auth-Service direkt mit. Registrierung, Login, Passwort-Reset, E-Mail-Verifizierung, OAuth-Provider (Google, GitHub, Apple etc.) und JWT-Ausstellung sind bereits implementiert und müssen nicht selbst gebaut werden. Verwaltet wird das Ganze über die systeminterne Tabelle `auth.users`, auf die eigener Anwendungscode nicht direkt zugreifen sollte.

> **Vorteil:** Deutlich weniger Eigenentwicklung bei Registrierung, Login und Token-Handling, da diese Logik vollständig von Supabase übernommen wird.

### 2.2 Trennung von `auth.users` und `public.profiles`

Da `auth.users` von Supabase verwaltet wird und nicht beliebig erweiterbar ist, werden alle anwendungsspezifischen Daten (Anzeigename, Avatar, Rollen, Einstellungen) in einer eigenen Tabelle `public.profiles` gehalten, die per Foreign Key 1:1 auf `auth.users.id` verweist. Diese Trennung ist der zentrale architektonische Baustein jeder Supabase-Benutzerverwaltung.

```sql
-- Verknüpfung Profile <-> Supabase Auth-User
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 2.3 Automatisches Anlegen von Profilen

Damit bei jeder Registrierung automatisch ein passender Profil-Datensatz entsteht, wird üblicherweise ein Datenbank-Trigger auf `auth.users` verwendet, der bei einem neuen Nutzer automatisch eine Zeile in `public.profiles` erzeugt.

```sql
-- Trigger: Profil automatisch bei Registrierung anlegen
CREATE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, display_name)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'display_name');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

## 3. Datenmodell

Das Datenmodell nutzt die von Supabase bereitgestellte `auth.users`-Tabelle als Basis und ergänzt sie um anwendungsspezifische Tabellen im `public`-Schema.

### 3.1 Tabelle: `public.profiles`

Erweitert `auth.users` um anwendungsspezifische Felder. E-Mail, Passwort-Hash und E-Mail-Verifizierung werden bereits vollständig von `auth.users` abgedeckt und müssen hier nicht dupliziert werden.

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | UUID, PK/FK | Verweist auf `auth.users.id` |
| display_name | VARCHAR(100) | Anzeigename |
| avatar_url | TEXT, NULL | Profilbild |
| status | ENUM | active, suspended, deleted |
| created_at | TIMESTAMPTZ | Erstellungszeitpunkt |
| updated_at | TIMESTAMPTZ | Letzte Änderung |

### 3.2 Tabelle: `roles` und `user_roles`

Rollen werden getrennt von Profilen gepflegt, um eine n:m-Beziehung (ein Benutzer kann mehrere Rollen haben) zu ermöglichen. Details und Beispiel-Policies hierzu in Kapitel 6.

| Tabelle | Spalten | Zweck |
|---|---|---|
| roles | id, name, description | Stammdaten der Rollen (z. B. admin, editor, viewer) |
| user_roles | user_id, role_id, assigned_at | Zuordnungstabelle (n:m), `user_id` referenziert `auth.users.id` |

### 3.3 Sessions und Refresh-Tokens

Supabase Auth verwaltet Access- und Refresh-Tokens bereits vollständig intern (Tabelle `auth.sessions` bzw. `auth.refresh_tokens`); eine eigene Session-Tabelle ist für den Standardfall nicht erforderlich. Wird eine erweiterte Geräteübersicht („Wo bin ich überall angemeldet?") benötigt, kann optional eine ergänzende Tabelle angelegt werden:

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | UUID | Primärschlüssel |
| user_id | UUID, FK | Verweis auf `auth.users.id` |
| user_agent | VARCHAR(255) | Für Geräteübersicht / „Angemeldete Geräte" |
| ip_address | VARCHAR(45) | Für Sicherheits-Logging |
| last_seen_at | TIMESTAMPTZ | Letzte Aktivität |

### 3.4 Tabelle: `audit_log` (optional, empfohlen)

Protokolliert sicherheitsrelevante Ereignisse wie Login-Versuche, Passwortänderungen oder Rollenänderungen – wichtig für Nachvollziehbarkeit und DSGVO-Auskunftsersuchen.

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | BIGINT | Primärschlüssel |
| user_id | UUID, FK | Betroffener Benutzer (`auth.users.id`) |
| event_type | VARCHAR(50) | z. B. login_success, login_failed, password_changed |
| metadata | JSONB | Zusätzlicher Kontext (IP, Gerät, etc.) |
| created_at | TIMESTAMPTZ | Zeitpunkt des Ereignisses |

---

## 4. Authentifizierungs-Flows

### 4.1 Registrierung

1. Client ruft `supabase.auth.signUp({ email, password })` auf
2. Supabase validiert E-Mail-Format und Passwortrichtlinie serverseitig
3. Passwort wird von GoTrue automatisch sicher gehasht (bcrypt) – eigener Code fasst das Passwort nie an
4. Eintrag wird in `auth.users` angelegt; per Trigger entsteht automatisch ein passender Datensatz in `public.profiles`
5. Bestätigungs-E-Mail mit zeitlich begrenztem Verifizierungslink wird von Supabase automatisch versendet
6. Nach Klick auf den Bestätigungslink wird `email_confirmed_at` in `auth.users` gesetzt

### 4.2 Login

1. Client ruft `supabase.auth.signInWithPassword({ email, password })` auf
2. GoTrue prüft das Passwort serverseitig gegen den gespeicherten Hash
3. Bei Erfolg stellt GoTrue automatisch ein JWT (Access-Token, Standard 1 Stunde) und einen Refresh-Token aus
4. Der Supabase-Client speichert beide Tokens automatisch (z. B. in localStorage/SecureStore je nach Plattform)
5. Fehlversuche werden von Supabase intern gezählt (Schutz vor Brute-Force, siehe Kapitel 5.3)

### 4.3 Token-Erneuerung (Refresh)

Der Supabase-Client erneuert abgelaufene Access-Tokens automatisch im Hintergrund über den Refresh-Token (Methode `supabase.auth.onAuthStateChange` / `autoRefreshToken`). Eine eigene Implementierung dieser Logik ist im Regelfall nicht notwendig. Bei kompromittierten Refresh-Tokens kann eine Session serverseitig über die Admin-API (`supabase.auth.admin.signOut`) widerrufen werden.

### 4.4 Passwort-Reset

1. Client ruft `supabase.auth.resetPasswordForEmail(email)` auf
2. Supabase erzeugt einmaligen, zeitlich begrenzten Reset-Link und versendet ihn per E-Mail
3. Nutzer öffnet den Link; die App ruft `supabase.auth.updateUser({ password })` mit der dadurch erzeugten Session auf
4. Der Reset-Link ist nach einmaliger Nutzung automatisch ungültig
5. Bestehende Sessions können bei Bedarf zusätzlich über die Admin-API widerrufen werden

### 4.5 OAuth / Social Login (optional)

Bei Supabase ist dies über GoTrue nativ konfigurierbar (Google, GitHub, Apple, Microsoft etc.) und wird über `supabase.auth.signInWithOAuth({ provider })` ausgelöst. Der jeweilige Provider-Account wird automatisch mit dem internen `auth.users`-Eintrag verknüpft; eine eigene `oauth_accounts`-Tabelle ist dafür nicht nötig.

---

## 5. Sicherheitskonzept

### 5.1 Passwort-Hashing

- Wird von Supabase Auth (GoTrue) automatisch mit bcrypt übernommen – eigener Anwendungscode kommt mit Klartext-Passwörtern nie in Kontakt
- Eigene Hash-Implementierungen oder das Speichern von Passwörtern in eigenen Tabellen sind nicht notwendig und sollten vermieden werden
- Mindestanforderungen an die Passwortstärke lassen sich im Supabase-Dashboard unter Authentication-Einstellungen konfigurieren

### 5.2 Token-Strategie

- Access-Token: JWT, von Supabase signiert, Standard-Gültigkeit 1 Stunde (im Dashboard konfigurierbar)
- Refresh-Token: wird vollständig von GoTrue verwaltet; bei Verwendung automatisch rotiert
- Tokens sollten clientseitig sicher abgelegt werden (z. B. Expo SecureStore auf Mobile, HttpOnly-Cookie bei SSR-Web-Apps statt localStorage)

### 5.3 Rate Limiting & Brute-Force-Schutz

- Supabase begrenzt Login- und Signup-Versuche bereits serverseitig pro IP/Account
- Zusätzliche Limits (z. B. pro Endpunkt) lassen sich über Supabase Edge Functions oder einen vorgeschalteten API-Gateway ergänzen
- CAPTCHA-Integration (z. B. hCaptcha) ist direkt im Supabase-Dashboard für Auth-Formulare aktivierbar

### 5.4 Row Level Security (RLS)

Postgres erlaubt es, Zugriffsregeln direkt auf Tabellenebene zu definieren, sodass ein Nutzer per Datenbank-Policy nur seine eigenen Daten lesen/schreiben kann – unabhängig vom Anwendungscode. RLS ist bei Supabase der zentrale Sicherheitsmechanismus, da der Supabase-Client direkt mit der Datenbank kommuniziert und es daher kein eigenes Backend gibt, das Zugriffe filtern könnte.

```sql
-- Beispiel: RLS-Policy für public.profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Nutzer sieht nur eigenes Profil"
ON public.profiles FOR SELECT
USING (auth.uid() = id);
```

> **Wichtig:** RLS muss auf jeder Tabelle, die über den Supabase-Client erreichbar ist, explizit aktiviert werden. Ohne aktivierte RLS-Policy ist eine Tabelle entweder komplett gesperrt oder – falls RLS nicht aktiviert wurde – ungeschützt für jeden authentifizierten Nutzer lesbar.

### 5.5 Transportsicherheit

- Ausschließlich TLS/HTTPS für alle Verbindungen zur Datenbank und API
- Supabase erzwingt SSL für alle Datenbankverbindungen standardmäßig

---

## 6. Rollen- und Rechtekonzept (RBAC)

Ein rollenbasiertes Zugriffsmodell (Role-Based Access Control) trennt die Frage „Wer ist der Nutzer?" (Authentifizierung, durch Supabase Auth gelöst) von „Was darf der Nutzer?" (Autorisierung). Bei Supabase wird Autorisierung in der Praxis fast vollständig über Row Level Security auf Datenbankebene abgebildet, da der Client direkt mit Postgres spricht und kein eigenes Backend zwischengeschaltet ist, das Rechte prüfen könnte.

### 6.1 Rollenmodell

Folgendes Rollenmodell wird als Ausgangspunkt empfohlen und lässt sich projektspezifisch erweitern:

| Rolle | Beschreibung |
|---|---|
| admin | Vollzugriff auf alle Daten, Benutzerverwaltung, Systemeinstellungen |
| editor | Erstellen und Bearbeiten von Inhalten, eingeschränkter Zugriff auf andere Nutzerdaten |
| viewer | Lesezugriff auf freigegebene Inhalte, voller Zugriff auf eigene Daten |

Jeder Benutzer kann grundsätzlich mehreren Rollen zugeordnet sein (n:m über `user_roles`); im einfachsten Fall reicht jedoch genau eine Rolle pro Nutzer.

### 6.2 Rechte-Matrix nach Ressource

Die folgende Matrix definiert konkret, welche Rolle welche Operation auf welcher Ressource ausführen darf. Sie ist die fachliche Grundlage für die RLS-Policies in Kapitel 6.4.

| Ressource | admin | editor | viewer |
|---|---|---|---|
| Eigenes Profil lesen/ändern | Ja | Ja | Ja |
| Fremde Profile lesen | Ja | Eingeschränkt | Nein |
| Fremde Profile ändern | Ja | Nein | Nein |
| Benutzer sperren/löschen | Ja | Nein | Nein |
| Rollen zuweisen | Ja | Nein | Nein |
| Eigene Inhalte erstellen | Ja | Ja | Nein |
| Fremde Inhalte bearbeiten | Ja | Nur freigegebene | Nein |
| Inhalte veröffentlichen | Ja | Ja | Nein |
| Audit-Log einsehen | Ja | Nein | Nein |

> Diese Matrix sollte vor der Implementierung gemeinsam mit den Fachverantwortlichen abgestimmt werden – sie ist die Spezifikation, aus der sich alle RLS-Policies direkt ableiten.

### 6.3 Helper-Funktion zur Rollenprüfung

Um nicht in jeder Policy einen komplexen Subquery gegen `user_roles` zu schreiben, empfiehlt sich eine wiederverwendbare SQL-Funktion, die prüft, ob der aktuell eingeloggte Nutzer eine bestimmte Rolle besitzt:

```sql
-- Helper-Funktion: hat der aktuelle Nutzer eine bestimmte Rolle?
CREATE FUNCTION public.has_role(role_name TEXT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles ur
    JOIN public.roles r ON r.id = ur.role_id
    WHERE ur.user_id = auth.uid()
      AND r.name = role_name
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;
```

### 6.4 RLS-Policies je Rolle

Auf Basis der Helper-Funktion lassen sich die Einträge aus der Rechte-Matrix direkt als Policies umsetzen. Beispiel für die Tabelle `public.profiles`:

```sql
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Jeder darf sein eigenes Profil lesen und ändern
CREATE POLICY "own_profile_select" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "own_profile_update" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Admins dürfen alle Profile lesen und ändern
CREATE POLICY "admin_profile_select" ON public.profiles
  FOR SELECT USING (public.has_role('admin'));

CREATE POLICY "admin_profile_update" ON public.profiles
  FOR UPDATE USING (public.has_role('admin'));
```

Analoges Beispiel für eine Inhaltstabelle (z. B. `posts`), bei der `editor` eigene Inhalte verwalten und `viewer` nur veröffentlichte Inhalte lesen darf:

```sql
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- Veröffentlichte Inhalte sind für alle authentifizierten Nutzer lesbar
CREATE POLICY "posts_select_published" ON public.posts
  FOR SELECT USING (status = 'published');

-- editor darf eigene Inhalte erstellen und bearbeiten
CREATE POLICY "posts_editor_manage_own" ON public.posts
  FOR ALL USING (
    auth.uid() = author_id AND public.has_role('editor')
  );

-- admin hat uneingeschränkten Zugriff
CREATE POLICY "posts_admin_all" ON public.posts
  FOR ALL USING (public.has_role('admin'));
```

### 6.5 Rechteprüfung im Frontend

RLS schützt zuverlässig die Datenbank, sollte aber nicht die einzige Stelle sein, an der Rechte sichtbar werden. Im Frontend wird die Rolle des eingeloggten Nutzers zusätzlich abgefragt (z. B. beim Login einmalig aus `user_roles` geladen), um UI-Elemente wie „Löschen"-Buttons oder Admin-Bereiche gezielt ein- oder auszublenden. Diese Prüfung dient ausschließlich der Usability – die eigentliche Absicherung erfolgt immer über RLS, da clientseitige Prüfungen umgangen werden können.

### 6.6 Admin-Bereich und Service-Role-Key

Für administrative Operationen, die bewusst RLS umgehen müssen (z. B. ein Admin-Dashboard, das alle Nutzer verwaltet), stellt Supabase einen Service-Role-Key bereit. Dieser darf ausschließlich serverseitig (z. B. in einer Supabase Edge Function oder einem eigenen Backend) verwendet werden und niemals im Client-Code oder in einer App-Auslieferung landen, da er sämtliche RLS-Policies aushebelt.

> **Sicherheitsregel:** Der Service-Role-Key ist gleichwertig mit einem Datenbank-Superuser-Passwort und gehört ausschließlich in serverseitige Umgebungsvariablen, niemals in Client-Bundles, Mobile Apps oder Versionskontrolle.

---

## 7. Datenschutz- und DSGVO-Aspekte

- Speicherung nur notwendiger personenbezogener Daten (Datenminimierung)
- Recht auf Auskunft: Export aller gespeicherten Nutzerdaten als JSON/CSV ermöglichen
- Recht auf Löschung: „Soft Delete" (Status `deleted` in `profiles`) plus definierter Prozess zur endgültigen Löschung des `auth.users`-Eintrags nach Aufbewahrungsfrist (`supabase.auth.admin.deleteUser`)
- Einwilligungs-Tracking bei Newsletter/Tracking-Cookies separat protokollieren
- Serverstandort/Region bei Projekterstellung in Supabase bewusst wählen (z. B. EU-Region für DSGVO-Konformität)

---

## 8. Zusammenfassung

Eine vollständige Benutzerverwaltung auf Supabase besteht aus denselben Grundbausteinen wie jede andere Benutzerverwaltung: einem klar definierten Datenmodell für Profile, Rollen und optionale Session-Metadaten, robusten Authentifizierungs-Flows, einer durchdachten Token-Strategie sowie einem detaillierten Rechtekonzept. Der entscheidende Unterschied liegt darin, dass Supabase Authentifizierung und Token-Handling über GoTrue vollständig übernimmt und Autorisierung über Row Level Security direkt auf Datenbankebene statt in einer eigenen Backend-Schicht abgebildet wird. Das reduziert den Implementierungsaufwand erheblich, verschiebt die wichtigste Sicherheitsarbeit aber explizit in die sorgfältige Definition der RLS-Policies aus Kapitel 6.
