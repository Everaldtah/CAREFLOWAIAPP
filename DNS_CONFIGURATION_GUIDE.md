# DNS Configuration Guide for careflowai.veraldlabs.co.uk

This guide explains how to configure the DNS for your CareFlow AI deployment.

---

## Overview

You need to configure DNS to point:
- **careflowai.veraldlabs.co.uk** → Frontend (Railway)
- **api.careflowai.veraldlabs.co.uk** → Backend API (Railway)

---

## Step 1: Get Your Railway URLs

After deploying to Railway, you'll receive URLs like:

```
Frontend: https://careflow-ai-abc123.up.railway.app
Backend:  https://careflow-api-xyz789.up.railway.app
```

Note these URLs for the next step.

---

## Step 2: Configure Custom Domains in Railway

### Add Frontend Domain

1. Go to https://railway.app/
2. Open your project
3. Click on the **Frontend** service
4. Go to **Settings** → **Domains**
5. Click **Generate Domain** to get a railway.app domain
6. Click **Add Custom Domain**
7. Enter: `careflowai.veraldlabs.co.uk`
8. Railway will show you DNS records to add

### Add Backend Domain

1. Click on the **Backend** service
2. Go to **Settings** → **Domains**
3. Click **Generate Domain** to get a railway.app domain
4. Click **Add Custom Domain**
5. Enter: `api.careflowai.veraldlabs.co.uk`
6. Railway will show you DNS records to add

---

## Step 3: Add DNS Records

### Option A: CNAME Records (Recommended)

Go to your VeraldLabs DNS management (where veraldlabs.co.uk is registered) and add:

| Type  | Name                      | Value                          | TTL  |
|-------|---------------------------|--------------------------------|------|
| CNAME | careflowai                | cname.railway.app              | 3600 |
| CNAME | api.careflowai            | cname.railway.app              | 3600 |

### Option B: Direct CNAME to Service

| Type  | Name                      | Value                                    | TTL  |
|-------|---------------------------|------------------------------------------|------|
| CNAME | careflowai                | [your-frontend].up.railway.app          | 3600 |
| CNAME | api.careflowai            | [your-backend].up.railway.app           | 3600 |

Replace `[your-frontend]` and `[your-backend]` with your actual Railway service names.

---

## Where to Add DNS Records

### If you registered veraldlabs.co.uk with:

#### GoDaddy
1. Login to GoDaddy
2. Go to **My Products** → **DNS Management**
3. Click **Add** next to the domain
4. Add the records above

#### Namecheap
1. Login to Namecheap
2. Go to **Domain List** → **Manage**
3. Go to **Advanced DNS**
4. Add the records above

#### Cloudflare
1. Login to Cloudflare
2. Select veraldlabs.co.uk
3. Go to **DNS** → **Records**
4. Add the records above

#### Your Hosting Provider (ProSiteHosting)
1. Login to your hosting control panel
2. Go to **Domains** → **Manage DNS**
3. Add the records above

---

## Step 4: Verify DNS Propagation

### Check DNS Records

```bash
# On Windows
nslookup careflowai.veraldlabs.co.uk
nslookup api.careflowai.veraldlabs.co.uk

# On Linux/Mac
dig careflowai.veraldlabs.co.uk
dig api.careflowai.veraldlabs.co.uk
```

### Online DNS Checker

Use: https://dnschecker.org/

Enter:
- `careflowai.veraldlabs.co.uk`
- `api.careflowai.veraldlabs.co.uk`

---

## Step 5: Wait for Propagation

DNS changes typically take:
- **10-30 minutes** for most providers
- **Up to 48 hours** in rare cases

Check propagation status at: https://dnschecker.org/

---

## Step 6: Verify SSL Certificates

Railway automatically provides SSL certificates for custom domains via Let's Encrypt.

To verify:
```bash
curl -I https://careflowai.veraldlabs.co.uk
```

Should return:
```
HTTP/2 200
server: railway
```

---

## DNS Record Types Explained

| Type | Purpose |
|------|---------|
| **CNAME** | Points a subdomain to another domain name (alias) |
| **A** | Points a subdomain to an IP address |
| **TXT** | Used for verification and SPF records |

We use CNAME because Railway uses dynamic IPs.

---

## Testing Your DNS Configuration

### Test Frontend
```bash
curl https://careflowai.veraldlabs.co.uk
```

Should return the CareFlow AI frontend HTML.

### Test Backend
```bash
curl https://api.careflowai.veraldlabs.co.uk/health
```

Should return: `{"status":"healthy"}`

### Test API Docs
Visit: https://api.careflowai.veraldlabs.co.uk/docs

---

## Troubleshooting

### DNS Not Propagating

1. Check you added the correct records
2. Wait 30 minutes and check again
3. Clear your DNS cache:
   ```bash
   # Windows
   ipconfig /flushdns

   # Mac
   sudo dscacheutil -flushcache

   # Linux
   sudo systemd-resolve --flush-caches
   ```

### "Site Not Found" Error

1. Verify DNS records are correct
2. Check Railway custom domain configuration
3. Wait for DNS propagation (up to 48 hours)

### SSL Certificate Error

1. Ensure DNS is propagated first
2. Check Railway custom domain status
3. Railway auto-generates SSL (may take 10-30 minutes)

### CNAME Not Working

1. Verify you're using CNAME (not A record)
2. Check the target domain is correct
3. Some providers don't allow CNAME for root domain (@)
   - This is fine, we're using subdomains only

---

## Complete DNS Example

After configuration, your DNS should look like:

| Type  | Name             | Value                      | TTL  |
|-------|------------------|----------------------------|------|
| A     | @                | [existing IP]              | 3600 |
| CNAME | www             | @                          | 3600 |
| CNAME | careflowai       | cname.railway.app          | 3600 |
| CNAME | api.careflowai   | cname.railway.app          | 3600 |

---

## Production Checklist

- [x] Railway frontend deployed
- [x] Railway backend deployed
- [x] Custom domains added in Railway
- [x] DNS records added at domain registrar
- [x] DNS propagated (check with dnschecker.org)
- [x] Frontend accessible at https://careflowai.veraldlabs.co.uk
- [x] Backend accessible at https://api.careflowai.veraldlabs.co.uk
- [x] SSL certificates active

---

## Summary of URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://careflowai.veraldlabs.co.uk |
| **Backend API** | https://api.careflowai.veraldlabs.co.uk |
| **API Documentation** | https://api.careflowai.veraldlabs.co.uk/docs |
| **Health Check** | https://api.careflowai.veraldlabs.co.uk/health |

---

## Next Steps

After DNS is configured:

1. Test frontend loads correctly
2. Test backend health endpoint
3. Test API documentation is accessible
4. Create admin user via frontend
5. Configure OpenAI API key in Railway

---

Need help?
- Railway DNS docs: https://docs.railway.app/reference/custom-domains
- DNS propagation checker: https://dnschecker.org/
