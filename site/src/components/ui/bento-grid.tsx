import { type ComponentPropsWithoutRef, type ReactNode } from "react"
import { ArrowRightIcon } from "@radix-ui/react-icons"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode
  className?: string
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string
  className: string
  background: ReactNode
  Icon?: React.ElementType
  description: string
  eyebrow?: string
  href?: string
  cta?: string
}

const BentoGrid = ({ children, className, ...props }: BentoGridProps) => {
  return (
    <div
      className={cn(
        "grid w-full auto-rows-[24rem] grid-cols-3 gap-5",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

const BentoCard = ({
  name,
  className,
  background,
  Icon,
  description,
  eyebrow,
  href,
  cta,
  ...props
}: BentoCardProps) => (
  <div
    key={name}
    className={cn(
      "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-3xl bg-fill",
      className
    )}
    {...props}
  >
    <div className="min-h-0 flex-1">{background}</div>
    <div className="p-6 sm:p-7">
      <div className="flex transform-gpu flex-col gap-1.5">
        {eyebrow && (
          <span className="text-xs font-semibold text-blue">{eyebrow}</span>
        )}
        {Icon && (
          <Icon className="h-10 w-10 origin-left transform-gpu text-blue transition-all duration-300 ease-in-out group-hover:scale-90" />
        )}
        <h3 className="text-xl font-semibold tracking-tight text-ink">
          {name}
        </h3>
        <p className="max-w-lg text-sm leading-relaxed text-ink-2">
          {description}
        </p>
      </div>

      {href && cta && (
        <div className="mt-3 flex w-full flex-row items-center">
          <Button
            variant="link"
            asChild
            size="sm"
            className="pointer-events-auto p-0 text-blue"
          >
            <a href={href}>
              {cta}
              <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
            </a>
          </Button>
        </div>
      )}
    </div>
  </div>
)

export { BentoCard, BentoGrid }
