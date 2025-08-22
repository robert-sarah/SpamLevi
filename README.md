# SpamLevi - Advanced WhatsApp Spam Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

SpamLevi est un outil avancé de spam WhatsApp conçu pour être plus performant, sécurisé et évolutif que les solutions existantes. Il offre des fonctionnalités avancées de gestion des requêtes, de limitation de taux et de journalisation sécurisée.

## ✨ Caractéristiques Principales

- **🔒 Sécurité Avancée**: Journalisation détaillée, rotation d'agents utilisateur, chiffrement des données
- **⚡ Performance Optimisée**: Traitement concurrent, limitation intelligente de taux, retry automatique
- **🎯 Interface Utilisateur**: CLI moderne avec interface Rich, barres de progression, statistiques en temps réel
- **📊 Monitoring Complet**: Statistiques détaillées, journalisation des tentatives, alertes de sécurité
- **⚙️ Configuration Flexible**: Fichier de configuration INI, variables d'environnement
- **🛡️ Protection Anti-Rate Limit**: Limitation intelligente des requêtes, cooldown automatique

## 🚀 Installation

### Méthode 1: Installation via pip
```bash
pip install spamlevi
```

### Méthode 2: Installation depuis la source
```bash
git clone https://github.com/spamlevi/spamlevi.git
cd spamlevi
pip install -r requirements.txt
python setup.py install
```

### Méthode 3: Installation développeur
```bash
git clone https://github.com/spamlevi/spamlevi.git
cd spamlevi
pip install -e .[dev]
```

## 📖 Utilisation

### Interface CLI Interactive
```bash
python spamlevi.py
```

### Mode Ligne de Commande
```bash
# Spam ciblé unique
python spamlevi.py --single

# Chargement depuis fichier
python spamlevi.py --file targets.txt

# Avec configuration personnalisée
python spamlevi.py --config custom_config.ini
```

### Utilisation Programmatique
```python
import asyncio
from spamlevi import SpamEngine, TargetManager, Config

async def main():
    config = Config()
    engine = SpamEngine(config)
    
    # Préparer les cibles
    targets = [
        {'phone': '+1234567890', 'message': 'Hello World', 'count': 10, 'delay': 1.0},
        {'phone': '+0987654321', 'message': 'Test message', 'count': 5, 'delay': 2.0}
    ]
    
    # Lancer le spam
    results = await engine.spam_multiple_targets(targets)
    
    # Afficher les statistiques
    stats = engine.get_statistics()
    print(stats)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Format du Fichier Cibles

Créez un fichier `targets.txt` avec le format suivant:
```
# Commentaires supportés
+1234567890,Hello World,10,1.0
+0987654321,Test message,5,2.5
+1112223333,Another message,3,1.5
```

Format: `phone_number,message,count,delay`

## ⚙️ Configuration

### Fichier config.ini
```ini
[rate_limit]
max_requests_per_minute = 30
max_requests_per_hour = 500
cooldown_period = 60
max_retries = 3
retry_delay = 5

[security]
enable_logging = true
log_level = INFO
encrypt_data = true
use_proxy = false
user_agent_rotation = true

[whatsapp]
api_url = https://web.whatsapp.com
send_endpoint = /send
timeout = 30
max_concurrent = 5
```

### Variables d'Environnement
```bash
export SPAMLEVI_LOG_LEVEL=DEBUG
export SPAMLEVI_MAX_CONCURRENT=10
export SPAMLEVI_TIMEOUT=60
```

## 📊 Statistiques et Monitoring

SpamLevi fournit des statistiques détaillées incluant:
- Nombre total de messages envoyés
- Messages échoués et rate-limited
- Messages par seconde
- Statistiques par numéro de téléphone
- Durée totale des opérations

## 🛡️ Sécurité

### Fonctionnalités de Sécurité
- **Journalisation sécurisée**: Logs détaillés avec rotation automatique
- **Protection contre les attaques**: Limitation de taux intelligente
- **Validation des entrées**: Vérification des numéros de téléphone et messages
- **Gestion des erreurs**: Gestion robuste des erreurs et retry automatique
- **Anonymat**: Rotation d'agents utilisateur et gestion des headers

### Bonnes Pratiques
- Utilisez toujours des délais raisonnables entre les messages
- Respectez les limites de WhatsApp
- Surveillez les logs pour les anomalies
- Testez sur de petites cibles avant de scaler

## 🧪 Tests

### Exécution des Tests
```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=spamlevi tests/

# Tests de performance
python -m pytest tests/performance/
```

### Tests de Sécurité
```bash
# Scan de sécurité
bandit -r spamlevi/

# Analyse de code
flake8 spamlevi/
```

## 🐛 Dépannage

### Problèmes Courants

**Erreur de connexion**:
```bash
# Vérifiez votre connexion internet
curl -I https://web.whatsapp.com
```

**Rate limiting excessif**:
- Réduisez `max_requests_per_minute` dans la configuration
- Augmentez les délais entre les messages

**Erreurs de validation**:
- Vérifiez le format des numéros de téléphone (+1234567890)
- Assurez-vous que les messages ne dépassent pas 4096 caractères

### Logs et Debugging
Les logs sont disponibles dans le dossier `logs/`:
- `security_YYYYMMDD.log`: Événements de sécurité
- `application.log`: Logs généraux
- `error.log`: Erreurs et exceptions

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez:
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Guidelines de Contribution
- Suivez PEP 8
- Ajoutez des tests pour les nouvelles fonctionnalités
- Documentez les changements dans README.md
- Assurez-vous que tous les tests passent

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Avertissement

**Utilisation Responsable**: Cet outil est destiné à des fins éducatives et de test uniquement. L'utilisation abusive peut enfreindre les conditions d'utilisation de WhatsApp et entraîner des restrictions de compte. L'utilisateur est responsable de l'utilisation conforme de cet outil.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/spamlevi/spamlevi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/spamlevi/spamlevi/discussions)
- **Email**: support@spamlevi.com

---

**SpamLevi - Advanced WhatsApp Spam Tool**  
*Sécurité, Performance, Évolutivité*