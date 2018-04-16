/*
 * Add a linux user using LDAP to look up their information.
 *
 * gcc RACcreateuser.c -o RACcreateuser -lldap -llber -lresolv
 *
 * may need to force 32-bit compile with
 *	gcc -m31 RACcreateuser.c -g -o RACcreateuser -L/usr/lib -lldap_r
 *
 * Typical User:
 *
 *       # RA00001, People, ROCK.org.gke
 *       dn: uid=RA00001,ou=People,dc=ROCK,dc=org,dc=gke
 *       objectClass: person
 *       objectClass: posixAccount
 *       objectClass: top
 *       cn: RA00001
 *       uid: RA00001
 *       sn: na
 *       uidNumber: 900001
 *       gidNumber: 12345
 *       userPassword: upw
 *       homeDirectory: na
 *       mail: email@company.com
 *
 *
 */
#define LDAP_DEPRECATED 1
#include <syslog.h>
#include <stdio.h>
#include <ldap.h>
#include <stdlib.h>
// Do we run the AT changelog script?
#undef CHANGE_LOGGING
//
//  Make sure you set _LDAPSERVER, _LDAPSEARCHBASE and _LDAPSECRET
//
//
//

const char *_LDAPSERVER = "10.10.1.236";
const char *_LDAPSEARCHBASE = "ou=People,dc=ROCK,dc=org,dc=gke";
const char _LDAPUSER[1024];
const char *_LDAPSECRET = "/etc/ldap.secret";


const char *INIT_HOME = "/home/%s";
const char *INIT_GROUP = "users";
const char *INIT_GROUPS = "";
const char *INIT_SHELL = "/bin/bash";

const char *useradd = "/usr/sbin/useradd";
const char *chfn = "/usr/bin/chfn";

#ifdef CHANGE_LOGGING
const char *changelog = "/root/changelog.sh";
#endif

/* lowercase a string */
void strlower(char *in, int max) {
    int x;
    int c;

    for (x = 0; x < strlen(in) && x < max; x++) {
        c = tolower((int) in[x]);
        in[x] = (char) c;
    }

    in[x] = '\0';
}


char *ltrim(char *s)
{
    while(isspace(*s)) s++;
    return s;
}

char *rtrim(char *s)
{
    char* back = s + strlen(s);
    while(isspace(*--back));
    *(back+1) = '\0';
    return s;
}

char *trim(char *s)
{
    return rtrim(ltrim(s));
}

int lookuprootdn() {
	int ret = 1;
	char *property_name="rootbinddn";
	char line[1024];
	FILE *input = fopen("/etc/ldap.conf","r");
	while(!feof(input)){
		fgets(line,1024,input);
		char *pos = strstr(line, property_name);
		if(pos!=NULL && pos==line){//startwith it
			strcpy(_LDAPUSER, trim(line+strlen(property_name)));
			ret = 0;
			break;
		}
	}
	fclose(input);
	return ret;
}


int main(int argc, char *argv[]) {
    LDAP *ld;
    LDAPMessage *result;
    int numfound, i;
    LDAPMessage *entry;
    BerElement *ptr;
    char *dn, *attr, **vals;
    char line[1024];
    char search_term[1024];

    char ldap_fullname[1024], ldap_usernumber[32], ldap_firstaccount[32],
        ldap_lcfirst[32], ldap_roomnumber[1024], ldap_phonenumber[1024];

    int ldap_account_index;

    char group[1024], groups[1024], home[1024], shell[1024];

    char syscall[1024];

    //Start syslog
    openlog ("RACcreateuser", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);
    syslog(LOG_NOTICE, "RACcreateuser started by User %d", getuid ());

    // Secret passwd file
    FILE *passwd;
    char _LDAPPASSWD[1024];

    // Get the ldap password
    if ((passwd = fopen(_LDAPSECRET, "r")) == NULL) {
        syslog(LOG_NOTICE, "FATAL: Could not open LDAP password file.");
        exit(1);
    }
    fgets(_LDAPPASSWD, 1024, passwd);
    if (_LDAPPASSWD[strlen(_LDAPPASSWD) - 1] == '\n')
        _LDAPPASSWD[strlen(_LDAPPASSWD) - 1] = '\0';
    fclose(passwd);

    //Get the user account
    if ( argc < 2 )
    {
	//No account specified on command line; ask the user for input.
        syslog(LOG_NOTICE, "FATAL: No USERID on input parm.");
        exit(2);
    }
    else
    {
	//Account specified on command line; convert it to char array.
	strcpy( line, argv[ 1 ] );
        strlower(line, strlen(line));
    }


    // If we have valid  user id
    if (strlen(line) < 4) {
        syslog(LOG_NOTICE, "FATAL: Invalid USERID: %s, Terminating.",line);
        exit(1);
    } else if ((strlen(line) <= 8 && strlen(line) >= 4)) {
        snprintf(search_term, 1024, "uid=%s", line);
    } else {
                syslog(LOG_NOTICE, "FATAL: Not a valid user account: User %s", line);
		exit(1);
	}

    //    printf("Got search term: '%s'\n", search_term);

	if(0!=lookuprootdn()){
                syslog(LOG_NOTICE, "failed to lookup rootdn.");
		exit(1);
	}

   //Get a handle to the server
     /* Get a handle to an LDAP connection. */

     if ( (ld = ldap_init( _LDAPSERVER, LDAP_PORT )) == NULL ) {
          perror( "ldap_initialize" );
          return( 1 );
     }

    int rc;
    int protocol_version = LDAP_VERSION3;
    rc = ldap_set_option(ld, LDAP_OPT_PROTOCOL_VERSION, &protocol_version);
    if (rc != LDAP_SUCCESS) {
        fprintf(stderr, "ldap_simple_bind_s: %s\n", ldap_err2string(rc));
        return(1);
    }


    // bind to it
    if (ldap_simple_bind_s(ld, _LDAPUSER, _LDAPPASSWD) != LDAP_SUCCESS) {
        ldap_perror(ld, "FATAL:  Could not bind to LDAP server");
        syslog(LOG_NOTICE, "FATAL: Could not bind to LDAP server");
        exit(1);
    }

    // search off the search_term we built above
    if (ldap_search_s(ld, _LDAPSEARCHBASE, LDAP_SCOPE_SUBTREE, search_term,
                      NULL, 0, &result) != LDAP_SUCCESS) {
        ldap_perror(ld, "FATAL:  Could not perform search");
        syslog(LOG_NOTICE, "FATAL: Could not perform search.");
        ldap_unbind(ld);
        exit(1);
    }

    // Did we find something
    if ((numfound = ldap_count_entries(ld, result)) == -1) {
        ldap_perror(ld, "FATAL:  Could not count search results");
        syslog(LOG_NOTICE, "FATAL: Could count search results.");
        ldap_unbind(ld);
        exit(1);
    }

    // Didn't find anyone.
    if (numfound == 0) {
        syslog(LOG_NOTICE, "FATAL: Could find user %s in LDAP.",line);
        ldap_unbind(ld);
        exit(3);
    } else {
        if (numfound > 1)
            printf("WARNING:  Multiple entries found for '%s'.  Using the first entry.\n", line);

        if ((entry = ldap_first_entry(ld, result)) == NULL) {
            printf("FATAL:  Could not get LDAP entry even though search returned true.\n");
            ldap_unbind(ld);
            exit(1);
        }

        // Extract first account value
        vals = ldap_get_values(ld, entry, "uid");
        if (vals == NULL) {
            printf("FATAL:  Could not get full name for user '%s'\n", line);
            ldap_unbind(ld);
            exit(1);
        } else {
            ldap_account_index = 0;

            snprintf(ldap_firstaccount, 32, vals[ldap_account_index]);
            strlower(ldap_firstaccount, 32);
        }
        ldap_value_free(vals);

        if (strcasecmp(line, ldap_firstaccount))
            printf("ALERT:  Please be aware that the PRIMARY account '%s' has been selected\n"
                   "for the account you attempted to create, '%s'.\n",
                   ldap_firstaccount, line);

        // Extract full name
        vals = ldap_get_values(ld, entry, "cn");
        if (vals == NULL) {
            printf("FATAL:  Could not get full name for user '%s'\n", line);
            ldap_unbind(ld);
            exit(1);
        } else {
            snprintf(ldap_fullname, 1024, vals[0]);
        }
        ldap_value_free(vals);

        vals = ldap_get_values(ld, entry, "uidNumber");
        if (vals == NULL) {
            printf("FATAL:  Could not get UID number for user '%s'\n", line);
            ldap_unbind(ld);
            exit(1);
        } else {
            snprintf(ldap_usernumber, 1024, vals[0]);
        }
        ldap_value_free(vals);

        vals = ldap_get_values(ld, entry, "roomnumber");
        if (vals == NULL) {
            snprintf(ldap_roomnumber, 1024, "");
        } else {
            snprintf(ldap_roomnumber, 1024, vals[0]);
        }
        ldap_value_free(vals);

        vals = ldap_get_values(ld, entry, "telephonenumber");
        if (vals == NULL) {
            snprintf(ldap_phonenumber, 1024, "");
        } else {
            snprintf(ldap_phonenumber, 1024, vals[0]);
        }
        ldap_value_free(vals);

        // Now we have all we need to know about them from ldap...
    }

    ldap_unbind(ld);

    // If we got this far without exiting then we have all the LDAP info and
    // we're ready to start populating the file...

    snprintf(group, 1024, INIT_GROUP);
    snprintf(groups, 1024, INIT_GROUPS);
    snprintf(home, 1024, INIT_HOME, ldap_firstaccount);
    snprintf(shell, 1024, INIT_SHELL);

    snprintf(syscall, 1024, "%s -d %s -m -g %s %s %s -s %s -u %s -p LDAP %s",
             useradd, home, group,
             strlen(groups) == 0 ? "" : "-G",
             groups, shell, ldap_usernumber,
             ldap_firstaccount);

    rc=system(syscall);
    if (rc >= 1) {
            syslog(LOG_NOTICE, "FATAL: USERADD failed with return code: %d.\n",rc);
            exit (6);
        } else {
            printf("%s\n",ldap_firstaccount);
            syslog(LOG_NOTICE, "Account %s created sucessfully.\n",ldap_firstaccount);
        }

// Change the "finger" information for the user.
    snprintf(syscall, 1024, "%s -f \"%s\" -o \"%s\" -w \"%s\" %s",
             chfn, ldap_fullname, ldap_roomnumber,
             ldap_phonenumber, ldap_firstaccount);
    system(syscall);

#ifdef CHANGE_LOGGING
    // Log to the changelog that we made this user
    snprintf(syscall, 1024, "%s LADDUSER Added user '%s' \"%s\"",
             changelog, ldap_firstaccount, ldap_fullname);
    system(syscall);
#endif
    printf("\nAccount created.\n");
    //Close syslog
    closelog ();
}
